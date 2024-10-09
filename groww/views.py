import datetime
import json
from _decimal import Decimal
from zoneinfo import ZoneInfo

from convert_to_requests import curl_to_requests, to_python_code

import requests
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response

from combo_investment import settings
from datahub.models import Security
from groww.models import GrowwRequestHeader, GrowwRequestError
from groww.serializers import (
    GrowwRequestSerializer,
    SchemeSearchSerializer,
    GrowwRequestGETSerializer,
    SchemeTransactionSerializer,
)
from mutual_funds.models import (
    Fund,
    FundInvestment,
    FundTransaction,
    FundInvestmentFolio,
    SIPDetails,
)
from mutual_funds.utils import create_fund_securities, get_or_create_security
from user_investment.models import Investment, BrokerTypeENUM, StockTransactions

# from mutual_funds.models import Fund
# from mutual_funds.serializers import FundSerializer
from users.models import User


class GrowwRequestException(Exception):
    def save(self):
        groww_request_error = GrowwRequestError(url=self.url)
        groww_request_error.data = json.loads(self.msg)
        groww_request_error.save()

    def __init__(self, url=None, msg=None, *args):
        super().__init__(*args)
        self.url = url
        self.msg = msg
        self.save()


class GrowwRequest:
    def __init__(self, user=None, http_method="get"):
        if user is None:
            user = User.objects.first()
        self.user = User.objects.first()
        groww_request_headers = GrowwRequestHeader.objects.filter(
            user=user, method=http_method
        ).last()
        if groww_request_headers is None:
            raise GrowwRequestException("Please Set Groww Request Headers first!")

        self._session = requests.Session()
        self._session.headers = groww_request_headers.headers

    def get_all_mf(self, page=0, size=20):
        url = settings.GROWW_MF_LIST
        response = self._session.get(
            url,
            params={
                "page": page,
                "size": size,
            },
        )
        if response.status_code != 200:
            raise GrowwRequestException(response.text)

        data = response.json()
        return data

    def get_mf_investment(self):
        # Required - GET headers
        url = settings.GROWW_MF_INVESTMENT_DASHBOARD

        response = self._session.get(url)

        if response.status_code != 200:
            raise GrowwRequestException(response.text)

        return response.json()

    def import_all_mf_funds(self, partial=True):
        mutual_funds = self.get_all_mf()
        print(mutual_funds)
        for mf in mutual_funds["content"]:
            from groww.tasks import create_or_update_groww_fund

            create_or_update_groww_fund.delay(mf["search_id"])
        return

    def create_or_update_fund(self, search_id):
        fund_details = self.get_scheme_details(search_id)

        fund = Fund.create_or_update_from_dict(fund_details)

        local_tz = ZoneInfo(settings.TIME_ZONE)
        if (
            datetime.datetime.now().astimezone(local_tz)
            - fund.last_updated.astimezone(local_tz)
        ).days > 5:
            holdings = fund_details.get("holdings")
            create_fund_securities(fund=fund, securities=holdings)
        fund.save()
        return fund

    def get_scheme_transactions(self, folio_number, scheme_code, page=0, size=100):
        # Required - GET headers
        query_params = {
            "folio_number": folio_number,
            "page": page,
            "scheme_code": scheme_code,
            "size": size,
        }

        url = settings.GROWW_SCHEME_TRANSACTIONS
        response = self._session.get(url, params=query_params)
        if response.status_code != 200:
            raise Exception((response.text, response.status_code))

        response = response.json()
        if response["response"] != "success":
            raise Exception(
                "Unable to fetch Scheme Transactions ->", folio_number, scheme_code
            )
        return response["data"]

    def get_scheme_details(self, search_id: str):
        url = settings.GROWW_MF_SCHEME_DETAILS + search_id
        response = self._session.get(url)
        if response.status_code != 200:
            raise GrowwRequestException(url=url, msg=response.text)

        return response.json()

    def get_stock_investment(self):
        url = settings.GROWW_STOCK_INVESTMENT_DASHBOARD

        response = self._session.get(url)

        if response.status_code != 200:
            raise GrowwRequestException(url, response.text)

        return response.json()

    def get_stock_investment_transactions(self, isin, till_date, page=0):
        url = settings.GROWW_STOCK_INVESTMENT_TRANSACTIONS.format(isin)
        all_transactions = []
        page = 0
        while page != -1:
            response = self._session.get(url, params={"page": page})
            if response.status_code != 200:
                raise GrowwRequestException(response.text)
            transactions = response.json()["data"]["transactions"]
            page += 1
            if len(transactions) > 0:
                last_transaction = transactions[-1]
                trade_date = datetime.datetime.strptime(
                    last_transaction.get("tradeDate"), "%Y-%m-%d"
                ).date()
                if till_date and till_date >= trade_date:
                    page = -1
            else:
                page = -1
            all_transactions.extend(transactions)

        return all_transactions


class GrowwInvestment:
    def __init__(self, user=None):
        self._user = user
        self._groww_request = GrowwRequest(user=self._user)

    def update_mf_funds(self):
        funds = Fund.objects.all()
        for fund in funds:
            self._groww_request.create_or_update_fund(fund.search_id)

    def import_mutual_funds(self):
        all_investments = self._groww_request.get_mf_investment()
        investments = all_investments.get("holdings")
        for investment in investments:
            self.process_investment(investment=investment)

    def process_investment(self, investment, partial_update=False):
        fund = self._groww_request.create_or_update_fund(investment.get("searchId"))

        fund_investment, created = FundInvestment.objects.get_or_create(
            fund_id=fund.id, user=self._user
        )
        units = Decimal(investment.get("units"))
        fund_investment.isin = investment.get("isin")
        fund_investment.current_value = investment.get("currentValue")
        fund_investment.xirr = investment.get("xirr")
        fund_investment.avg_nav = investment.get("averageNav")
        fund_investment.amount_invested = investment.get("amountInvested")
        fund_investment.units = units
        fund_investment.save()

        self.process_investment_folios(
            fund_investment=fund_investment, investment=investment
        )

    def process_investment_folios(self, fund_investment, investment):
        if investment.get("hasMultipleFolio"):
            folios = investment.get("folios")
            for folio in folios:
                folio_number = folio.get("folioNumber")
                units = folio.get("units")
                amount_invested = folio.get("amountInvested")
                average_nav = float(folio.get("averageNav"))
                current_value = folio.get("currentValue")
                folio_type = folio.get("folioType")
                xirr = folio.get("xirr")
                portfolio_source = folio.get("portfolioSource")
                first_unrealised_purchase_date = datetime.datetime.strptime(
                    folio.get("firstUnrealisedPurchaseDate"), "%Y-%m-%dT%H:%M:%S"
                ).date()
                sip_data = folio.get("sipDetails")
                sip_details = SIPDetails(
                    has_active_sip=sip_data.get("hasActiveSip"),
                    active_sip_count=sip_data.get("activeSipCount"),
                )
                sip_details.save()

                (
                    fund_investment_folio,
                    created,
                ) = FundInvestmentFolio.objects.update_or_create(
                    folio_number=folio_number,
                    defaults={
                        "units": units,
                        "amount_invested": amount_invested,
                        "average_nav": average_nav,
                        "current_value": current_value,
                        "xirr": xirr,
                        "portfolio_source": portfolio_source,
                        "folio_type": folio_type,
                        "first_unrealised_purchase_date": first_unrealised_purchase_date,
                        "sip_details": sip_details,
                        "user": self._user,
                    },
                )
                fund_investment.folios.add(fund_investment_folio)
        else:
            folio_number = investment.get("folioNumber")
            units = investment.get("units")
            amount_invested = investment.get("amountInvested")
            average_nav = investment.get("averageNav")
            current_value = investment.get("currentValue")
            folio_type = investment.get("folioType")
            xirr = investment.get("xirr")
            portfolio_source = investment.get("source")
            first_unrealised_purchase_date = None
            sip_data = investment.get("sipDetails")
            sip_details = SIPDetails(
                has_active_sip=sip_data.get("hasActiveSip"),
                active_sip_count=sip_data.get("activeSipCount"),
            )
            sip_details.save()

            fund_investment_folio = FundInvestmentFolio(
                folio_number=folio_number,
                units=units,
                amount_invested=amount_invested,
                average_nav=average_nav,
                current_value=current_value,
                xirr=xirr,
                portfolio_source=portfolio_source,
                folio_type=folio_type,
                first_unrealised_purchase_date=first_unrealised_purchase_date,
                sip_details=sip_details,
                user=self._user,
            )

            fund_investment_folio.save()
            fund_investment.folios.add(fund_investment_folio)

    def create_fund_investment(self, investment, fund):
        fund_investment, created = FundInvestment.objects.get_or_create(
            fund_id=fund.id, user=self._user
        )
        units = Decimal(investment.get("units"))
        fund_investment.isin = investment.get("isin")
        fund_investment.current_value = investment.get("currentValue")
        fund_investment.xirr = investment.get("xirr")
        fund_investment.avg_nav = investment.get("averageNav")
        fund_investment.units = units
        fund_investment.save()

    def process_fund_transactions(self, fund_investment):
        fund_investment_folios = fund_investment.folios.all()
        for fund_investment_folio in fund_investment_folios:
            page = 0
            while page != -1:
                scheme_transactions = self._groww_request.get_scheme_transactions(
                    folio_number=fund_investment_folio.folio_number,
                    scheme_code=fund_investment.fund.scheme_code,
                    page=page,
                )
                total_pages = int(scheme_transactions.get("total_pages"))
                if page < total_pages:
                    page += 1
                else:
                    page = -1

                transactions = scheme_transactions.get("transaction_list")

                fund_transactions = fund_investment.transactions.all()
                for transaction in transactions:
                    db_transaction = fund_transactions.filter(
                        user_id=self._user.id,
                        transaction_id=transaction.get("transaction_id"),
                        user_account_id=transaction.get("user_account_id"),
                    ).last()
                    if db_transaction is None:
                        transaction["user_id"] = self._user.id
                        db_transaction = FundTransaction.create_from_dict(transaction)
                        db_transaction.user = self._user
                        fund_investment.transactions.add(db_transaction)
                        db_transaction.save()
                fund_investment.save()

    def process_stock_investment(self, holding):
        symbol_data = holding.get("symbolData")
        holding_data = holding.get("holding")

        isin = symbol_data.get("symbolIsin")

        security = Security.objects.get(isin=isin)

        user_investment, created = Investment.objects.update_or_create(
            broker=BrokerTypeENUM.groww.name,
            security=security,
            defaults={
                "quantity": holding_data.get("holdingQty"),
                "avg_price": holding_data.get("holdingAvgPrice") / 100,
                "security": security,
            },
        )

        print(created, security, holding_data.get("holdingQty"))

        last_transaction = (
            StockTransactions.objects.filter(investment_id=user_investment.id)
            .order_by("-trade_date")
            .first()
        )

        last_transaction_date = (
            (last_transaction.trade_date - datetime.timedelta(days=1))
            if last_transaction
            else None
        )

        investment_transactions = self._groww_request.get_stock_investment_transactions(
            isin=isin, till_date=last_transaction_date
        )

        self.create_or_update_stock_transaction(
            transactions=investment_transactions, investment=user_investment
        )

    def create_or_update_stock_transaction(self, transactions, investment):
        for transaction in transactions:
            lookup_fields = {
                "investment": investment,
                "transaction_id": BrokerTypeENUM.groww.name
                + str(investment.id)
                + f"_{transaction.get('txnId')}",
            }

            update_fields = {
                "quantity": transaction["qty"],
                "price": int(transaction["price"]) / 100,
                "trade_date": datetime.datetime.strptime(
                    transaction.get("tradeDate"), "%Y-%m-%d"
                ).date(),
                "type": transaction["type"],
                "data": transaction,
            }
            StockTransactions.objects.update_or_create(
                defaults=update_fields, **lookup_fields
            )

        return

    def import_stock_investment(self):
        all_investments = self._groww_request.get_stock_investment()
        investments = all_investments.get("holdings")
        for investment in investments:
            self.process_stock_investment(holding=investment)


@extend_schema(tags=["GrowwRequest"])
class GrowwRequestHeaderViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        return GrowwRequestGETSerializer

    def get_queryset(self):
        return GrowwRequestHeader.objects.all()

    def perform_create(self, serializer):
        headers = serializer.validated_data.get("headers")
        req = curl_to_requests(headers)
        headers = req.headers
        serializer.validated_data["headers"] = headers
        serializer.save()


@extend_schema(tags=["Groww"])
class GrowwRequestViewSet(viewsets.ViewSet):
    @action(
        name="Get MF Investment",
        url_name="get_mf_dashboard",
        url_path="get_mf_dashboard",
        detail=False,
    )
    def get_mf_dashboard(self, request, *args, **kwargs):
        groww = GrowwRequest()
        result = groww.get_mf_investment()

        return Response(result)

    @extend_schema(parameters=[SchemeSearchSerializer])
    @action(
        name="GET Scheme Details",
        url_name="scheme_details",
        url_path="scheme_details",
        detail=False,
    )
    def get_scheme_details(self, request, *args, **kwargs):
        user = User.objects.first()
        groww = GrowwRequest(user, "get")
        request_data = SchemeSearchSerializer(data=request.query_params)
        if not request_data.is_valid():
            raise Exception(request_data.errors)

        result = groww.get_scheme_details(
            request_data.validated_data.get("search_id"),
        )
        return Response(result)

    @extend_schema(parameters=[SchemeTransactionSerializer])
    @action(
        name="GET Scheme Transaction",
        url_name="scheme_transactions",
        url_path="scheme_transactions",
        detail=False,
    )
    def get_scheme_transactions(self, request, *args, **kwargs):
        groww = GrowwRequest()
        params = SchemeTransactionSerializer(data=request.query_params)
        if not params.is_valid():
            raise Exception(params.errors)
        params_data = params.validated_data
        result = groww.get_scheme_transactions(
            params_data.get("folio_number"),
            params_data.get("scheme_code"),
            params_data.get("page"),
            params_data.get("size"),
        )

        return Response(result)

    @action(
        name="Add Groww Investment",
        url_name="add_groww_investment",
        url_path="add_groww_investment",
        detail=False,
    )
    def add_groww_investment(self, *args, **kwargs):
        user = User.objects.first()
        groww = GrowwRequest(user, "post")
        mf_investment = groww.get_mf_investment()

        holdings = mf_investment.get("holdings")
        created_funds = []
        for holding in holdings:
            # fund = Fund.create_from_dict(holding)
            # created_funds.append(fund)
            pass
        return
        # serialized_holdings = FundSerializer(created_funds, many=True).data
        # return Response(serialized_holdings, status=status.HTTP_201_CREATED)

import datetime
import time
from _decimal import Decimal, ROUND_DOWN, ROUND_UP, ROUND_HALF_UP
from collections import defaultdict
from zoneinfo import ZoneInfo

import django_filters
import logging
from django.db.models import Q
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.shortcuts import render
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from combo_investment import settings
from combo_investment.exception import APIBadRequest
from data_import.models import TradeBook
from data_import.serializers import TradeBookSerializer
from datahub.models import Security, Parameter
from datahub.serializers import SecuritySerializerForSectorWisePortfolio
from industries.views import get_basic_industry_object_from_industry_info
from scrapper.views import NSEScrapper
from user_investment.models import Investment, BrokerInvestment
from user_investment.serializer import InvestmentSerializer
from user_investment.utils import (
    get_securities_by_sector,
    get_security_percentage_change,
)

logger = logging.Logger("UserInvestment")


class UserInvestment:
    def __init__(self, user=None, headers=None, include=None):
        """
        :param user:
        :param headers:
        :param include: One of two choices ->
            both - for processing both processed and investment_processed
            investment_processed - for processing investment_processed
            default - for processing processed
        """
        process_filters = Q(processed=False)
        if include == "both":
            process_filters = Q(Q(processed=False) | Q(investment_processed=False))
        elif include == "investment_processed":
            process_filters = Q(investment_processed=False)
        self.tradebooks_to_process = (
            TradeBook.objects.filter(user=user)
            .filter(process_filters)
            .order_by("execution_datetime")
        )
        self.user = user
        self.headers = headers
        self.nse = NSEScrapper()
        self._error_in_update_all_securities = False
        self._errors_in_securities = list()
        self._bulk_updated_securities = []
        self.historical_price_info_mapping = {
            "open": "CH_OPENING_PRICE",
            "vwap": "VWAP",
            "close": "CH_CLOSING_PRICE",
            "lastPrice": "CH_LAST_TRADED_PRICE",
            "previousClose": "CH_PREVIOUS_CLS_PRICE",
            "intraDayHighLow": {
                "max": "CH_TRADE_HIGH_PRICE",
                "min": "CH_TRADE_LOW_PRICE",
                "value": "CH_CLOSING_PRICE",
            },
        }

    def process_trade_books(self):
        for trade_book in self.tradebooks_to_process:
            symbol = self.nse.get_symbol(trade_book.security)
            if not symbol:
                continue
            security = Security.objects.filter(symbol=symbol).last()
            if security is None:
                security = Security(symbol=symbol)

            # Update security
            self.update_security(security)
            trade_book.processed = True

            broker_investment = self.create_broker_investment(
                tradebook=trade_book, security=security
            )
            self.update_user_investment(
                trade_book=trade_book,
                security=security,
                broker_investment=broker_investment,
            )
            trade_book.investment_processed = True
            trade_book.save()

    def create_broker_investment(self, tradebook, security):
        broker_investment = BrokerInvestment(
            security_id=security.id,
            quantity=tradebook.quantity,
            avg_price=tradebook.net_rate,
            user=self.user,
            broker=tradebook.broker,
            execution_datetime=tradebook.execution_datetime,
            trade_book=tradebook,
        )
        broker_investment.save()
        return broker_investment

    def update_security(self, security, bulk_update=False):
        quote, status_code = self.nse.get_quote_by_symbol(security.symbol)
        if status_code != 200:
            print("Error", quote)
            if bulk_update:
                self._error_in_update_all_securities = True
                self._errors_in_securities.append({"id": security.id, "error": quote})
            return quote, status_code

        # Industry data
        industry_info = quote.get("industryInfo")
        basic_industry = get_basic_industry_object_from_industry_info(industry_info)
        if not security.basic_industry:
            security.basic_industry = basic_industry

        # Price data
        price_info = quote.get("priceInfo")
        today_date = datetime.datetime.now().date().isoformat()
        historical_price_info = security.historical_price_info
        historical_price_info[today_date] = price_info
        security.historical_price_info = historical_price_info

        # Info
        info = quote.get("info")
        if not security.isin:
            security.isin = info.get("isin")
        if not security.name:
            security.name = info.get("companyName")

        # Security Info
        security_info = quote.get("securityInfo")
        if not security.security_info:
            security.security_info = security_info

        # Metadata Info
        metadata = quote.get("metadata")
        security.metadata = metadata

        security.last_updated_price = price_info.get("lastPrice")
        local_tz = ZoneInfo(settings.TIME_ZONE)
        security.price_modified_datetime = datetime.datetime.now().astimezone(local_tz)
        # logger.info(security.price_modified_datetime, "price_modified_datetime")
        security.save()
        # logger.info(security.price_modified_datetime, "price_modified_datetime")
        return quote, status_code

    def update_all_securities(self, securities):
        for security in securities:
            security, status_code = self.update_security(security, bulk_update=True)
            self._bulk_updated_securities.append(security)

        return self._bulk_updated_securities, self._errors_in_securities

    def update_user_investment(self, trade_book, security, broker_investment):
        user_investment = Investment.objects.filter(
            user=self.user, security=security
        ).last()
        if user_investment is None:
            user_investment = Investment(user=self.user, security=security)

        old_quantity = user_investment.quantity or 0
        old_avg_price = user_investment.avg_price or 0
        print(trade_book.id, security.id, trade_book.buy_sell.lower())
        if trade_book.buy_sell.lower() in ["b", "buy"]:
            new_quantity = trade_book.quantity
            net_rate = Decimal(trade_book.net_rate)
            rounded_net_rate = net_rate.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            new_avg_price = abs(rounded_net_rate)
            new_cost = new_avg_price * new_quantity
            old_cost = old_avg_price * old_quantity

            avg_price = (new_cost + old_cost) / (old_quantity + new_quantity)
            user_investment.avg_price = avg_price
            user_investment.buying_prices.append(
                {"net_rate": trade_book.net_rate, "quantity": trade_book.quantity}
            )
            new_quantity = user_investment.quantity + trade_book.quantity
        else:
            new_quantity = user_investment.quantity - abs(trade_book.quantity)
            user_investment.selling_prices.append(
                {"net_rate": trade_book.net_rate, "quantity": trade_book.quantity}
            )

        user_investment.quantity = new_quantity
        print(user_investment.quantity, "user investment ......")
        user_investment.save()
        user_investment.broker_investments.add(broker_investment)
        user_investment.save()

    def update_security_for_historical_prices(self, security_id, from_year=1980):
        security = Security.objects.filter(id=security_id).last()
        logger.info(
            f"Updating {security.symbol} for historical prices from year {from_year}"
        )
        from_date = datetime.datetime(from_year, 1, 1)
        today_date = datetime.datetime.now()
        historical_db_price_info = security.historical_price_info

        while from_date < today_date:
            to_date = from_date + datetime.timedelta(days=365)
            print(from_date, "->", to_date)
            data, status = self.nse.get_historical_data_by_symbol(
                security.symbol, from_date, to_date
            )
            from_date = to_date

            if status == 200:
                historical_db_price_info = (
                    self.update_historical_info_for_day_to_db_field(
                        historical_db_price_info, data
                    )
                )

        security.historical_price_info = historical_db_price_info
        security.save()
        logger.info(
            f"Updated {security.symbol} for historical prices from year {from_year}"
        )

        return security

    def update_historical_info_for_day_to_db_field(
        self, historical_db_price_info, market_data
    ):

        history = self.historical_price_info_mapping
        intraday_day = self.historical_price_info_mapping["intraDayHighLow"]
        already_exists_date_values = historical_db_price_info.keys()

        for historical_info in market_data["data"]:
            if historical_info.get("CH_TIMESTAMP") in already_exists_date_values:
                print(f"Skipped for date {historical_info.get('CH_TIMESTAMP')}")
                continue
            local_history = {}
            local_intraday_data = {}
            for k, v in history.items():
                if k == "intraDayHighLow":
                    for intraday_key, intraday_value in intraday_day.items():
                        local_intraday_data[intraday_key] = historical_info.get(
                            intraday_value
                        )
                else:
                    local_history[k] = historical_info.get(v)

            historical_db_price_info[historical_info.get("CH_TIMESTAMP")] = {
                "intraDayHighLow": local_intraday_data,
                **local_history,
            }

        return historical_db_price_info

    def performance(self, broker="all"):
        if broker == "all":
            user_investments = Investment.objects.filter(quantity__gt=0)
        else:
            user_investments = Investment.objects.filter(
                quantity__gt=0, broker_investments__broker=broker
            ).distinct()

        if self.user:
            user_investments = user_investments.filter(user=self.user)

        top_gainers_security_changes = []
        top_losers_security_changes = []
        for investment in user_investments:
            res = get_security_percentage_change(investment, broker=broker)
            serialized_security = SecuritySerializerForSectorWisePortfolio(
                investment.security
            ).data
            if res.get("p_change") > 0:
                top_gainers_security_changes.append(
                    {"security": serialized_security, **res}
                )
            else:
                top_losers_security_changes.append(
                    {"security": serialized_security, **res}
                )

        gainers_sorted_security_changes = sorted(
            top_gainers_security_changes,
            key=lambda item: item["p_change"],
            reverse=True,
        )
        losers_sorted_security_changes = sorted(
            top_losers_security_changes, key=lambda item: item["p_change"]
        )
        res = {
            "top_gainers": gainers_sorted_security_changes[:5],
            "top_losers": losers_sorted_security_changes[:5],
        }

        return res


class InvestmentFilter(FilterSet):
    symbol = django_filters.CharFilter(method="filter_by_security_symbol")
    broker = django_filters.ChoiceFilter(
        choices=(("Groww", "Groww"), ("Zerodha", "Zerodha"), ("All", "All")),
        method="filter_by_broker",
    )

    def filter_by_broker(self, queryset, name, value):
        return queryset

    # name = django_filters.CharFilter(field_name="name", lookup_expr="contains")
    # id = django_filters.CharFilter(method="filter_by_ids")
    #
    def filter_by_security_symbol(self, queryset, name, value):
        symbols = value.split(",")
        return queryset.filter(security__symbol__in=symbols)

    class Meta:
        model = Investment
        fields = ("id", "symbol")


@extend_schema(tags=["Investment App"])
class InvestmentViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = InvestmentFilter

    def get_serializer_class(self):
        logger.warning(self.request.query_params)
        if self.action in ["list"]:
            return InvestmentSerializer
        return InvestmentSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        kwargs["context"]["broker"] = self.request.query_params.get("broker", None)
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        broker = self.request.query_params.get("broker", None)
        if broker is None or broker.lower() == "all":
            qs = Investment.objects.filter(quantity__gt=0)
        else:
            qs = Investment.objects.filter(broker_investments__broker=broker).distinct()

        filter_qs = self.filter_queryset(qs)

        return filter_qs

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=["GET"],
        name="Investment Info",
        url_name="info",
    )
    def info(self, *args, **kwargs):
        broker = self.request.query_params.get("broker", None)
        user_investment = UserInvestment()
        qs = self.get_queryset()
        logger.warning(qs.values_list("id", flat=True))
        day_change = {}
        one_day_changes = []
        total_investment_value = 0
        total_current_value = 0

        for investment in qs:
            total_investment_value += investment.calculate_amount_invested(
                broker=broker
            )
            total_current_value += investment.calculate_current_value(broker=broker)
            security = investment.security
            security_data = get_security_percentage_change(investment, broker=broker)
            day_change[security.symbol] = security_data

            one_day_changes.append(security_data.get("total_change"))

        amount_invested = Decimal(total_investment_value).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        total_returns = total_current_value - amount_invested
        logger.warning((total_returns, amount_invested, "asjdf;lkjas;fk;kasdf"))
        percentage_returns = Decimal((total_returns / amount_invested) * 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        one_day_change = Decimal(sum(one_day_changes)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        logger.warning((one_day_change / amount_invested) * 100)
        one_day_percentage_returns = (
            (one_day_change / amount_invested) * 100
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_returns = total_returns.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        current_value = Decimal(total_current_value).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        data = {
            "amount_invested": format(amount_invested, ","),
            "total_returns": f"{total_returns}",
            "total_preturns": percentage_returns,
            "one_day_change": f"{one_day_change}",
            "one_day_pchange": one_day_percentage_returns,
            "current_value": format(current_value, ","),
            "day_change": day_change,
            "sector_wise_portfolio": get_securities_by_sector(qs, broker=broker),
            "performance": user_investment.performance(broker=broker),
        }

        return Response(data=data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["GET"],
        name="Investment Info",
        url_name="sector_allocation",
        url_path="sector_allocation",
    )
    def get_sector_allocation(self, *args, **kwargs):
        broker = self.request.query_params.get("broker", None)
        qs = self.get_queryset()
        # logger.warning("-------------------")
        # logger.warning(qs)
        # logger.warning(broker)
        # logger.warning("-------------------")

        data = get_securities_by_sector(
            qs, show_zero_allocation_sectors=False, broker=broker
        )
        return Response(data=data, status=status.HTTP_200_OK)


class TransactionFilter(FilterSet):
    # symbol = django_filters.CharFilter(method="filter_by_security_symbol")

    # name = django_filters.CharFilter(field_name="name", lookup_expr="contains")
    # id = django_filters.CharFilter(method="filter_by_ids")
    #
    # def filter_by_security_symbol(self, queryset, name, value):
    #     symbols = value.split(",")
    #     return queryset.filter(security__symbol__in=symbols)

    class Meta:
        model = TradeBook
        fields = (
            "id",
            "symbol",
            "buy_sell",
            "broker",
            "processed",
            "investment_processed",
            "user",
            "execution_datetime",
        )


@extend_schema(tags=["Transaction App"], methods=["GET", ""])
class TransactionViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TransactionFilter

    def get_queryset(self):
        qs = TradeBook.objects.all()
        filtered_qs = self.filter_queryset(qs)
        last_trade_book = filtered_qs.order_by("execution_datetime").last()
        trade_books = TradeBook.objects.none()
        if last_trade_book is not None:
            date = last_trade_book.execution_datetime.date()
            trade_books = filtered_qs.filter(execution_datetime__date=date)
        return trade_books

    def get_serializer_class(self):
        return TradeBookSerializer

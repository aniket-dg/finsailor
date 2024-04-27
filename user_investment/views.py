import datetime
from _decimal import Decimal
import django_filters
from django.db.models import Q
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.shortcuts import render
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from data_import.models import TradeBook
from datahub.models import Security
from industries.views import get_basic_industry_object_from_industry_info
from scrapper.views import NSEScrapper
from user_investment.models import Investment
from user_investment.serializer import InvestmentSerializer


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
        self.tradebooks_to_process = TradeBook.objects.filter(
            user=user, exchange__iexact="nse"
        ).filter(process_filters)
        self.user = user
        self.headers = headers
        self.nse = NSEScrapper(headers=headers)
        self._error_in_update_all_securities = False
        self._errors_in_securities = list()
        self._bulk_updated_securities = []

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

            self.update_user_investment(trade_book=trade_book, security=security)
            trade_book.investment_processed = True
            trade_book.save()

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
        security.price_modified_datetime = datetime.datetime.now()
        security.save()
        return security, status_code

    def update_all_securities(self, securities):
        for security in securities:
            security, status_code = self.update_security(security, bulk_update=True)
            self._bulk_updated_securities.append(security)

        return self._bulk_updated_securities, self._errors_in_securities

    def update_user_investment(self, trade_book, security):
        user_investment = Investment.objects.filter(
            user=self.user, security=security
        ).last()
        if user_investment is None:
            user_investment = Investment(user=self.user, security=security)

        old_quantity = user_investment.quantity or 0
        old_avg_price = user_investment.avg_price or 0

        if trade_book.buy_sell.lower() in ["b", "buy"]:
            new_quantity = trade_book.quantity
            new_avg_price = abs(Decimal(trade_book.net_rate))
            new_cost = new_avg_price * new_quantity
            old_cost = old_avg_price * old_quantity

            avg_price = (new_cost + old_cost) / (old_quantity + new_quantity)
            user_investment.avg_price = avg_price
            user_investment.buying_prices.append(trade_book.net_rate)
            new_quantity = user_investment.quantity + trade_book.quantity
        else:
            new_quantity = user_investment.quantity - trade_book.quantity
            user_investment.selling_prices.append(trade_book.net_rate)

        user_investment.quantity = new_quantity
        user_investment.save()

    def change_in_value(self, to_date, security_id):
        """
        This function return the change and pChange to to_date value of particular security
        :param to_date:
        :param security_id:
        :return:
        {
            change: decimal
            pchange: float
        }
        """
        security = Security.objects.filter(id=security_id)
        historical_price_info = security.historical_price_info


class InvestmentFilter(FilterSet):
    symbol = django_filters.CharFilter(method="filter_by_security_symbol")

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
        return InvestmentSerializer

    def get_queryset(self):
        qs = Investment.objects.all()

        filter_qs = self.filter_queryset(qs)

        return filter_qs

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=["GET"],
        name="Investment Info",
        url_name="info",
    )
    def info(self, *args, **kwargs):
        qs = self.get_queryset()

        total_investment_value = (
            qs.annotate(
                total_value=ExpressionWrapper(
                    F("avg_price") * F("quantity"),
                    output_field=DecimalField(decimal_places=2, max_digits=12),
                )
            ).aggregate(total_investment_value=Sum("total_value"))[
                "total_investment_value"
            ]
            or 0
        )

        current_value = (
            qs.annotate(
                total_value=ExpressionWrapper(
                    F("security__last_updated_price") * F("quantity"),
                    output_field=DecimalField(decimal_places=2, max_digits=12),
                )
            ).aggregate(total_investment_value=Sum("total_value"))[
                "total_investment_value"
            ]
            or 0
        )

        data = {
            "amount_invested": total_investment_value,
            "current_value": current_value,
        }

        return Response(data=data, status=status.HTTP_200_OK)

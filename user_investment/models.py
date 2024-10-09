import json
from _decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from enum import Enum

from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import QuerySet, Manager, ExpressionWrapper, F, DecimalField, Sum, Avg
from django.db.models.functions import TruncMonth

from data_import.models import TradeBook, BrokerEnum
from datahub.models import Security, CustomJSONEncoder
from users.models import User


class InvestmentQuerySet(QuerySet):
    def with_related(self):
        return self.select_related(
            "security__basic_industry__industry__sector__macro_sector"
        )


class InvestmentManager(models.Manager):
    def get_queryset(self):
        return InvestmentQuerySet(self.model, using=self._db).with_related()


class BrokerTypeENUM(Enum):
    groww = "Groww"
    zerodha = "Zerodha"


class Investment(models.Model):
    BROKER_TYPES = ((field.name, field.value) for field in BrokerTypeENUM)

    security = models.ForeignKey(
        Security,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="investments",
    )
    quantity = models.IntegerField(default=0)
    avg_price = models.DecimalField(
        decimal_places=4, null=True, blank=True, max_digits=12
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    broker = models.CharField(choices=BROKER_TYPES, default=BrokerTypeENUM.groww.name)
    objects = Manager()
    select_related = InvestmentManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["broker", "security", "user"],
                name="unique_broker_security_user",
            )
        ]


class SectorWisePortfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    broker = models.CharField(max_length=100)
    datetime = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict, encoder=CustomJSONEncoder)

    def flatten(self, sector_data):
        res = []
        data = sector_data["data"]
        for k, v in data.items():
            res.append({
                "name": k,
                'allocation': v["metadata"]["allocation"],
                'amount_invested': v["metadata"]["amount_invested"],
                'no_of_stocks': v["metadata"]["no_of_stocks"]
            })
        return res

    def flatten_data(self):
        res = {}
        data = self.data["data"]
        for sector_name, sector_data in data.items():
            res[sector_name] = self.flatten(sector_data)

        return res



class TransactionTypeENUM(Enum):
    credit = "Credit"
    debit = "Debit"


class StockTransactions(models.Model):
    """
    transaction_id : it must contain broker name with transaction id
    e.g.,
    for groww - groww_investmentid_txnId
    for zerodha - zerodha_investmentid_order_id
    """

    TRANSACTION_TYPES = ((field.name, field.value) for field in TransactionTypeENUM)
    investment = models.ForeignKey(
        Investment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(decimal_places=4, null=True, blank=True, max_digits=12)
    type = models.CharField(
        choices=TRANSACTION_TYPES, max_length=100, help_text="Transaction type"
    )
    trade_date = models.DateField()
    data = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    transaction_id = models.CharField(unique=True)
    BrokerTypes = ((field.name, field.value) for field in BrokerEnum)
    broker = models.CharField(
        max_length=100, choices=BrokerTypes, default="groww"
    )

    @staticmethod
    def get_amount_invested(qs):
        return float(
                qs.annotate(
                    total_value = ExpressionWrapper(
                        F("price")*F("quantity"),
                        output_field=DecimalField(decimal_places=2, max_digits=12)
                    )
                ).aggregate(total_investment_value=Sum("total_value"))[
                    "total_investment_value"
                ]
                or 0
        )

    @staticmethod
    def get_amount_invested_per_month(qs):
        return (
            qs.annotate(
                total_value=ExpressionWrapper(
                    F("price") * F("quantity"),
                    output_field=DecimalField(decimal_places=2, max_digits=12)
                ),
                month=TruncMonth("trade_date")
            )
            .values("month")
            .annotate(total_investment_value=Sum("total_value"))
            .order_by("month")
        )

    @staticmethod
    def get_amount_invested_with_returns(qs, month_date):
        market_value = 0
        for transaction in qs:
            market_value += transaction.investment.security.get_last_price_for_month(month_date) * transaction.quantity

        return StockTransactions.get_amount_invested(qs), market_value


    @staticmethod
    def get_amount_invested_per_month_per_investment_security(qs):
        """
        Get the total amount invested per month for each investment associated with a security.

        :param qs: A queryset of StockTransactions
        :return: A queryset with total investment per month per investment
        """

        security_ids = qs.values_list("investment__security_id", flat=True).distinct("investment__security_id")
        securities = Security.objects.filter(id__in=security_ids)

        securities_by_ids = {security.id: security for security in securities}

        amount_invested_per_month_per_security = (
            qs.annotate(
                total_value=ExpressionWrapper(
                    F("price") * F("quantity"),
                    output_field=DecimalField(decimal_places=2, max_digits=12)
                ),
                month=TruncMonth("trade_date")
            )
            .values("investment__security_id", "month")
            .annotate(
                total_investment_value=Sum("total_value"),
                total_quantity=Sum("quantity"),  # Include the total quantity here
                avg_price=Avg("price")
            )
            .order_by("investment__security_id", "month")
        )

        res = defaultdict(lambda: defaultdict(int))

        for amount_invested_per_month in amount_invested_per_month_per_security:
            security = securities_by_ids.get(amount_invested_per_month["investment__security_id"])
            security_last_price = security.get_last_price_for_month(amount_invested_per_month["month"])
            quantity = amount_invested_per_month["total_quantity"]

            res[amount_invested_per_month["month"].strftime("%b-%Y")]["market_value"] += quantity * security_last_price
            res[amount_invested_per_month["month"].strftime("%b-%Y")]["invested_value"] += float(amount_invested_per_month["total_investment_value"])

        return res



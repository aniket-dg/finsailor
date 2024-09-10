import json
from _decimal import Decimal, ROUND_HALF_UP
from enum import Enum

from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import QuerySet, Manager

from data_import.models import TradeBook
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

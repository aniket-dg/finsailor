from json import JSONEncoder

from django.db import models
from django.utils.translation import gettext_lazy as _
from bsedata.bse import BSE
import datetime
import decimal

from industries.models import BasicIndustry


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return float(obj)


class SecurityCache(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)


class Security(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    isin = models.CharField(max_length=100, null=True, blank=True)
    scrip_code = models.CharField(max_length=100, null=True, blank=True)
    symbol = models.CharField(max_length=100, unique=True)
    last_updated_price = models.DecimalField(
        decimal_places=2, null=True, blank=True, max_digits=6
    )
    price_modified_datetime = models.DateTimeField(blank=True, null=True)
    basic_industry = models.ForeignKey(
        BasicIndustry, on_delete=models.SET_NULL, null=True, blank=True
    )
    historical_price_info = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    security_info = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    metadata = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )

    def __str__(self):
        return f"Security - {self.name}"


# class ActionType(models.TextChoices):
#     B = ("B", _("Buy"))
#     S = ("S", _("Sell"))
#     buy = ("Buy", _("Buy"))
#     sell = ("S", _("Sell"))


class ExchangeType(models.TextChoices):
    BSE = ("BSE", _("Bombay Stock Exchange"))
    NSE = ("NSE", _("National Stock Exchange"))


class Exchange(models.Model):
    name = models.CharField(
        choices=ExchangeType.choices, max_length=50, default=ExchangeType.BSE
    )


class Broker(models.Model):
    name = models.CharField(max_length=50)

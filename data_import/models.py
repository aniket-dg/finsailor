from enum import Enum

from django.db import models

from datahub.models import Security, Exchange, Broker
from users.models import User


class BrokerEnum(Enum):
    groww = "Groww"
    zerodha = "Zerodha"


class UploadedContractNotePDF(models.Model):
    BrokerTypes = ((field.name, field.value) for field in BrokerEnum)
    pdf_file = models.FileField(upload_to="pdf_files/contract_notes/")
    broker = models.CharField(
        max_length=100, choices=BrokerTypes, null=True, blank=True
    )
    password = models.CharField(max_length=100, null=True, blank=True)
    processed = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)


class UploadedDematReportPDF(models.Model):
    BrokerTypes = ((field.name, field.value) for field in BrokerEnum)
    pdf_file = models.FileField(upload_to="pdf_files/demat_reports/")
    broker = models.CharField(
        max_length=100, choices=BrokerTypes, null=True, blank=True
    )
    password = models.CharField(max_length=100, null=True, blank=True)
    processed = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)


class TradeBook(models.Model):
    symbol = models.CharField(max_length=100, null=True, blank=True)
    isin = models.CharField(max_length=100, null=True, blank=True)
    execution_datetime = models.DateTimeField(null=True, blank=True)
    order_no = models.CharField(unique=True, max_length=100)
    security = models.CharField(max_length=100, null=True, blank=True)
    exchange = models.CharField(max_length=100, null=True, blank=True)
    buy_sell = models.CharField(default="B", max_length=10)
    quantity = models.IntegerField(default=0)
    gross_rate = models.CharField(max_length=20, null=True, blank=True)
    brokerage = models.CharField(max_length=20, null=True, blank=True)
    net_rate = models.CharField(max_length=20, null=True, blank=True)
    closing_rate = models.CharField(max_length=20, null=True, blank=True)
    total = models.CharField(max_length=20, null=True, blank=True)
    remarks = models.CharField(max_length=100, null=True, blank=True)
    broker = models.CharField(max_length=100, default="Groww")
    processed = models.BooleanField(default=False)
    investment_processed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class InvestmentBook(models.Model):
    security = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    processed = models.BooleanField(default=False)
    investment_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.security}"

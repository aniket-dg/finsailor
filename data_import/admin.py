from django.contrib import admin

from data_import.models import (
    TradeBook,
    InvestmentBook,
    UploadedContractNotePDF,
    UploadedDematReportPDF,
)
from datahub.models import Broker


# Register your models here.


@admin.register(TradeBook)
class TradeBookAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "execution_datetime",
        "security",
        "buy_sell",
        "quantity",
        "order_no",
        # "processed",
        # "investment_processed",
    ]

    list_filter = [
        "buy_sell",
        "processed",
        "investment_processed",
        "execution_datetime",
        "security",
    ]


@admin.register(InvestmentBook)
class ModelNameAdmin(admin.ModelAdmin):
    list_display = ["id", "security", "quantity", "processed", "investment_processed"]


# admin.site.register(InvestmentBook)
admin.site.register(Broker)
admin.site.register(UploadedContractNotePDF)
admin.site.register(UploadedDematReportPDF)

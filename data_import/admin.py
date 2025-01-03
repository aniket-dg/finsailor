from django.contrib import admin

from data_import.models import (
    TradeBook,
    InvestmentBook,
    UploadedContractNotePDF,
    UploadedDematReportPDF,
    MutualFundBook,
    UploadedMutualFundReport,
)
from datahub.models import Broker


# Register your models here.


@admin.register(TradeBook)
class TradeBookAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "execution_datetime",
        "security",
        "broker",
        "buy_sell",
        "quantity",
        "order_no",
        # "processed",
        # "investment_processed",
    ]

    list_filter = [
        "user",
        "broker",
        "buy_sell",
        "processed",
        "investment_processed",
        "execution_datetime",
        "security",
    ]


@admin.register(InvestmentBook)
class InvestmentBookAdmin(admin.ModelAdmin):
    list_display = ["id", "security", "quantity", "processed", "investment_processed"]


@admin.register(MutualFundBook)
class MutualFundBookAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "scheme_name",
        "transaction_type",
        "nav",
        "units",
        "date",
        "investment_processed",
    ]
    list_filter = ["scheme_name"]


admin.site.register(Broker)
admin.site.register(UploadedContractNotePDF)
admin.site.register(UploadedDematReportPDF)
admin.site.register(UploadedMutualFundReport)

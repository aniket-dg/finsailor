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
    list_display = ["id", "order_no", "security", "processed", "investment_processed"]


@admin.register(InvestmentBook)
class ModelNameAdmin(admin.ModelAdmin):
    list_display = ["id", "security", "quantity", "processed", "investment_processed"]


# admin.site.register(InvestmentBook)
admin.site.register(Broker)
admin.site.register(UploadedContractNotePDF)
admin.site.register(UploadedDematReportPDF)

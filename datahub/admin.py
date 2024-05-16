from django.contrib import admin
from django.db.models import JSONField

from combo_investment.admin_utils import JSONEditor
from datahub.models import (
    Security,
    Exchange,
    Parameter,
    StockIndex,
    TodayStockIndex,
    GeneralInfo,
)


# Register your models here.


@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "basic_industry"]
    formfield_overrides = {JSONField: {"widget": JSONEditor}}
    list_filter = ["basic_industry"]


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(StockIndex)
class StockIndexAdmin(admin.ModelAdmin):
    list_display = ["id", "key", "index", "indexSymbol", "date", "time"]


@admin.register(TodayStockIndex)
class TodayStockIndexAdmin(admin.ModelAdmin):
    filter_horizontal = ["stocks_indices"]
    list_display = ["id", "date", "time"]


@admin.register(GeneralInfo)
class GeneralInfoAdmin(admin.ModelAdmin):
    list_display = ["id", "tradebook_last_uploaded"]

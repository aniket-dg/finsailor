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
    Holiday,
)
from django.utils.translation import gettext_lazy as _

class MonthFilter(admin.SimpleListFilter):
    title = _('month')
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        # Generate a list of months with transactions
        months = set()
        for holiday in model_admin.model.objects.all():
            months.add(holiday.trading_date.strftime('%Y-%m'))
        return [(month, month) for month in sorted(months)]

    def queryset(self, request, queryset):
        if self.value():
            year, month = self.value().split('-')
            return queryset.filter(trading_date__year=year, trading_date__month=month)
        return queryset

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


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ["id", "trading_date", "description", "weekday"]
    list_filter = [MonthFilter]

from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from datahub.models import Security
from mutual_funds.models import (
    FundInvestment,
    Fund,
    FundSecurity,
    FundTransaction,
    FundInvestmentFolio,
)


# Register your models here.
@admin.register(FundInvestment)
class FundInvestmentAdmin(admin.ModelAdmin):
    list_display = ["id", "fund", "avg_nav","units"]


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "scheme_name",
    ]


class SecurityFilter(SimpleListFilter):
    title = "Security"
    parameter_name = "security"

    def lookups(self, request, model_admin):
        security_ids = FundSecurity.objects.all().values_list("security_id", flat=True)
        securities = Security.objects.filter(id__in=security_ids)
        return [(s.id, s.name) for s in securities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(security_id=self.value())
        return queryset

@admin.register(FundSecurity)
class FundSecurityAdmin(admin.ModelAdmin):
    list_display = ["id", "fund", "security", "corpus_per"]
    list_filter = ["fund", SecurityFilter]


from django.utils.translation import gettext_lazy as _
class MonthFilter(admin.SimpleListFilter):
    title = _('month')
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        # Generate a list of months with transactions
        months = set()
        for transaction in model_admin.model.objects.all():
            months.add(transaction.transaction_date.strftime('%Y-%m'))
        return [(month, month) for month in sorted(months)]

    def queryset(self, request, queryset):
        if self.value():
            year, month = self.value().split('-')
            return queryset.filter(transaction_date__year=year, transaction_date__month=month)
        return queryset


@admin.register(FundTransaction)
class FundTransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "folio_number", "transaction_date","user", "transaction_amount", "units"]
    list_filter = ["user", "transaction_date", MonthFilter]


@admin.register(FundInvestmentFolio)
class FundInvestmentFolioAdmin(admin.ModelAdmin):
    list_display = ["id", "units","user", "folio_number"]
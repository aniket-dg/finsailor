from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from datahub.models import Security
from mutual_funds.models import FundInvestment, Fund, FundSecurity


# Register your models here.
@admin.register(FundInvestment)
class FundInvestmentAdmin(admin.ModelAdmin):
    list_display = ["id", "fund", "avg_nav", "units"]


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
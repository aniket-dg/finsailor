from django.contrib import admin

from datahub.models import Security
from user_investment.models import Investment, SectorWisePortfolio
from django.contrib.admin import SimpleListFilter


class SecurityFilter(SimpleListFilter):
    title = "Security"
    parameter_name = "security"

    def lookups(self, request, model_admin):
        security_ids = Investment.objects.all().values_list("security_id", flat=True)
        securities = Security.objects.filter(id__in=security_ids)
        return [(s.id, s.name) for s in securities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(security_id=self.value())
        return queryset


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "security",
        "broker",
        "avg_price",
        "quantity",
        "user",
        "get_basic_industry",
    ]

    list_filter = ["broker", SecurityFilter, "user"]

    def get_basic_industry(self, obj):
        return obj.security.basic_industry

    get_basic_industry.short_description = "Basic Industry"


admin.site.register(SectorWisePortfolio)

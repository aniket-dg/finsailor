from django.contrib import admin

from user_investment.models import Investment

# Register your models here.
# admin.site.register(Investment)


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "security",
        "avg_price",
        "quantity",
        "get_basic_industry",
    ]

    def get_basic_industry(self, obj):
        return obj.security.basic_industry

    get_basic_industry.short_description = "Basic Industry"

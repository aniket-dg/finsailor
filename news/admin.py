from django.contrib import admin

from news.models import StockEvent


# Register your models here.
@admin.register(StockEvent)
class StockEventAdmin(admin.ModelAdmin):
    list_display = ["id", "company", "purpose"]

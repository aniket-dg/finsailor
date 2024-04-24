from django.contrib import admin

from datahub.models import Security, Exchange


# Register your models here.


@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(Exchange)
class SecurityAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]

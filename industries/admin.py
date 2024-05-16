from django.contrib import admin
from .models import *

# Register your models here.
# admin.site.register(MacroSector)
# admin.site.register(Sector)
# admin.site.register(Industry)
# admin.site.register(BasicIndustry)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "macro_sector"]


@admin.register(MacroSector)
class ModelNameAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "mes_code",
        "name",
    ]


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ["id", "ind_code", "name", "sector"]
    list_filter = ["sector"]


@admin.register(BasicIndustry)
class BasicIndustryAdmin(admin.ModelAdmin):
    list_display = ["id", "basic_ind_code", "name", "industry"]

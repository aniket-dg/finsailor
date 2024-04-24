from django.shortcuts import render

from industries.models import BasicIndustry


def get_basic_industry_object_from_industry_info(industry_info):
    macro = industry_info.get("macro")
    sector = industry_info.get("sector")
    industry = industry_info.get("industry")
    basic_industry_name = industry_info.get("basicIndustry")

    basic_industry = BasicIndustry.objects.filter(
        name__iexact=basic_industry_name,
        industry__name__iexact=industry,
        industry__sector__name__iexact=sector,
        industry__sector__macro_sector__name__iexact=macro,
    ).last()

    return basic_industry

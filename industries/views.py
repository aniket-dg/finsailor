import datetime

from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from datahub.models import Security
from industries.models import BasicIndustry
from industries.serializers import MacroSectorSerializer
from user_investment.utils import calculate_todays_performance_by_macro_sector


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


def find(industry_info):
    macro = industry_info.get("macro")
    sector = industry_info.get("sector")
    industry = industry_info.get("industry")
    basic_industry_name = industry_info.get("basicIndustry")

    basic_industry = BasicIndustry.objects.filter(
        name__iexact=basic_industry_name
    ).last()
    if basic_industry is None:
        return "Basic Industry", basic_industry_name

    basic_industry = BasicIndustry.objects.filter(
        name__iexact=basic_industry_name,
        industry__name__iexact=industry,
    ).last()
    if basic_industry is None:
        return "Industry", industry

    basic_industry = BasicIndustry.objects.filter(
        name__iexact=basic_industry_name,
        industry__name__iexact=industry,
        industry__sector__name__iexact=sector,
    ).last()

    if basic_industry is None:
        return "Sector", sector

    basic_industry = BasicIndustry.objects.filter(
        name__iexact=basic_industry_name,
        industry__name__iexact=industry,
        industry__sector__name__iexact=sector,
        industry__sector__macro_sector__name__iexact=macro,
    ).last()
    if basic_industry is None:
        return "macro_sector", macro

    return "PResent"


@extend_schema(tags=["Industry App"])
class MacroSectorViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        return MacroSectorSerializer

    @action(
        detail=False,
        methods=["GET"],
        name="sector_performance",
        url_name="sector_performance",
    )
    def get_sector_performance(self, *args, **kwargs):
        securities = Security.objects.filter(security_info__tradingStatus="Active")
        sector_performance = calculate_todays_performance_by_macro_sector(
            securities=securities
        )
        # sector_performance["date"] = datetime.datetime.now()
        return Response(sector_performance, status=status.HTTP_200_OK)

import logging

import django_filters
from django.db.models import Q
from django.shortcuts import render
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from combo_investment.pagination import PageNumberPaginationForSecurity
from datahub.models import Security, GeneralInfo, StockIndex
from datahub.serializers import (
    SecuritySerializer,
    UpdateSecuritySerializer,
    SecurityFilterSerializer,
    HistoricalPricesForSecurity,
    GeneralInfoSerializer,
    StockIndexSerializer, SecurityNameSerializer,
)
from user_investment.views import UserInvestment
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger("Datahub")

class SecurityFilter(FilterSet):
    symbol = django_filters.CharFilter(field_name="symbol", lookup_expr="iexact")
    name_or_symbol = django_filters.CharFilter(method="filter_name_or_symbol_with_min_length")
    name = django_filters.CharFilter(field_name="name", lookup_expr="contains")
    id = django_filters.CharFilter(method="filter_by_ids")
    limit = django_filters.NumberFilter()
    details = django_filters.BooleanFilter(method="filter_details")

    def filter_details(self, queryset, name, value):
        return queryset

    def filter_by_ids(self, queryset, name, value):
        ids = value.split(",")
        return queryset.filter(id__in=ids)

    def filter_name_or_symbol_with_min_length(self, queryset, name, value):
        logger.info(value, "value")
        if len(value) < 3:
            raise ValidationError(_("Name must be at least 3 characters long"))
        return queryset.filter(Q(name__icontains=value)|Q(symbol__icontains=value))

    class Meta:
        model = Security
        fields = ("id", "symbol", "name")


@extend_schema(tags=["Datahub App"])
class SecurityViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SecurityFilter
    pagination_class = PageNumberPaginationForSecurity

    def get_serializer_class(self):
        # if self.action in ["update_security"]:
        #     return UpdateSecuritySerializer
        details = self.request.query_params.get("details", False)
        if not details:
            return SecurityNameSerializer
        return SecuritySerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Security.objects.none()

        qs = Security.objects.all()
        details = self.request.query_params.get("details", False)

        if not details:
            return qs.only("id", "name")

        return qs

    def perform_create(self, serializer):
        serializer.save()

    # @extend_schema()
    @action(
        detail=True,
        methods=["GET"],
        name="update_security",
        url_name="update_security",
    )
    def update_security(self, request, *args, **kwargs):
        security = self.get_object()
        user_investment = UserInvestment()
        security, status_code = user_investment.update_security(security)
        res = {"status": status_code}
        if status_code != 200:
            res["errors"] = security
        else:
            res["data"] = SecuritySerializer(security).data
        return Response(data=res, status=status.HTTP_200_OK)

    @extend_schema(
        request=SecurityFilterSerializer,
        responses={"errors": [], "data": SecuritySerializer(many=True)},
    )
    @action(
        detail=False,
        methods=["POST"],
        name="update_all_securities",
        url_name="update_all_securities",
    )
    def update_all_securities(self, request, *args, **kwargs):
        security_serializer = UpdateSecuritySerializer(data=request.data)
        security_serializer.is_valid(raise_exception=True)
        headers = security_serializer.validated_data.get("headers")

        qs = self.get_queryset()
        filter_qs = self.filter_queryset(qs)

        user_investment = UserInvestment(headers=headers)
        updated_securities, errors = user_investment.update_all_securities(filter_qs)

        return Response(
            {
                "data": SecuritySerializer(updated_securities, many=True).data,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(parameters=[HistoricalPricesForSecurity])
    @action(
        detail=True,
        methods=["GET"],
        name="update_historical_prices",
        url_name="update_historical_prices",
    )
    def update_historical_prices(self, request, *args, **kwargs):
        security = self.get_object()
        from_year = int(self.request.query_params.get("from_year", 1980))

        user_investment = UserInvestment()
        updated_security = user_investment.update_security_for_historical_prices(
            security.id, from_year=from_year
        )

        serialized_security_data = SecuritySerializer(updated_security).data
        return Response(serialized_security_data, status=status.HTTP_200_OK)


@extend_schema(tags=["General Info"])
class GeneralInfoViewSet(viewsets.ModelViewSet):
    queryset = GeneralInfo.objects.all()
    serializer_class = GeneralInfoSerializer


class StockIndexViewSet(viewsets.ModelViewSet):
    queryset = StockIndex.objects.all()
    serializer_class = StockIndexSerializer

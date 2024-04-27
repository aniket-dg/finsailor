import django_filters
from django.shortcuts import render
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from datahub.models import Security
from datahub.serializers import (
    SecuritySerializer,
    UpdateSecuritySerializer,
    SecurityFilterSerializer,
)
from user_investment.views import UserInvestment


class SecurityFilter(FilterSet):
    symbol = django_filters.CharFilter(field_name="symbol", lookup_expr="iexact")
    name = django_filters.CharFilter(field_name="name", lookup_expr="contains")
    id = django_filters.CharFilter(method="filter_by_ids")

    def filter_by_ids(self, queryset, name, value):
        ids = value.split(",")
        return queryset.filter(id__in=ids)

    class Meta:
        model = Security
        fields = ("id", "symbol", "name")


@extend_schema(tags=["Datahub App"])
class SecurityViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SecurityFilter

    def get_serializer_class(self):
        if self.action in ["update_security"]:
            return UpdateSecuritySerializer

        return SecuritySerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Security.objects.none()
        return Security.objects.all()

    def perform_create(self, serializer):
        serializer.save()

    @extend_schema(request=UpdateSecuritySerializer)
    @action(
        detail=True,
        methods=["POST"],
        name="update_security",
        url_name="update_security",
    )
    def update_security(self, request, *args, **kwargs):
        security_serializer = UpdateSecuritySerializer(data=request.data)
        security_serializer.is_valid(raise_exception=True)
        headers = security_serializer.validated_data.get("headers")
        security = self.get_object()
        user_investment = UserInvestment(headers=headers)
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

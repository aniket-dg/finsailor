import json

import requests
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from combo_investment import settings
from groww.models import GrowwRequestHeader
from groww.serializers import GrowwRequestSerializer, SchemeSearchSerializer
from users.models import User


class GrowwRequest:
    def __init__(self, user=None, http_method="get"):
        groww_request_headers = GrowwRequestHeader.objects.filter(
            user=user, method=http_method
        ).last()
        if groww_request_headers is None:
            raise Exception("Please Set Groww Request Headers first!")

        self._session = requests.Session()
        self._session.headers = groww_request_headers.headers

    def get_mf_investment(self):
        url = settings.GROWW_MF_INVESTMENT_DASHBOARD

        response = self._session.get(url)

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    def get_scheme_details(self, scheme_isin, scheme_type):
        body = json.dumps({"isin": scheme_isin, "schemeType": scheme_type})
        url = settings.GROWW_MF_SCHEME_DETAILS

        response = self._session.post(url, data=body)

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()


@extend_schema(tags=["Groww"])
class GrowwRequestViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        return GrowwRequestSerializer

    @action(
        name="Get MF Investment",
        url_name="get_mf_dashboard",
        url_path="get_mf_dashboard",
        detail=False,
    )
    def get_mf_dashboard(self, request, *args, **kwargs):
        user = User.objects.last()
        groww = GrowwRequest(user)

        result = groww.get_mf_investment()

        return Response(result)

    @extend_schema(parameters=[SchemeSearchSerializer])
    @action(
        name="GET Scheme Details",
        url_name="scheme_details",
        url_path="scheme_details",
        detail=False,
    )
    def get_scheme_details(self, request, *args, **kwargs):
        user = User.objects.last()
        groww = GrowwRequest(user, "post")
        request_data = SchemeSearchSerializer(data=request.query_params)
        if not request_data.is_valid():
            raise Exception(request_data.errors)

        result = groww.get_scheme_details(
            request_data.validated_data.get("isin"),
            request_data.validated_data.get("scheme_type"),
        )
        return Response(result)

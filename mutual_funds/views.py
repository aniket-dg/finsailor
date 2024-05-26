import logging
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from mutual_funds.models import FundInvestment
from mutual_funds.serializers import FundInvestmentSerializer

logger = logging.getLogger("MutualFunds")


@extend_schema(tags=["Mutual Fund Investment App"], methods=["GET", ""])
class FundInvestmentViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        return FundInvestmentSerializer

    def get_queryset(self):
        return FundInvestment.objects.all()
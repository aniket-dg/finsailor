import logging

from django.db.models import Sum
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from mutual_funds.models import FundInvestment
from mutual_funds.serializers import FundInvestmentSerializer

logger = logging.getLogger("MutualFunds")


@extend_schema(tags=["Mutual Fund Investment App"], methods=["GET", ""])
class FundInvestmentViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        return FundInvestmentSerializer

    def get_queryset(self):
        return FundInvestment.objects.all()

    @action(detail=False, url_name="info", url_path="info")
    def info(self, *args, **kwargs):
        investments = self.get_queryset()
        total_amount_invested = investments.aggregate(Sum("amount_invested"))[
            "amount_invested__sum"
        ]
        current_value = investments.aggregate(Sum("current_value"))[
            "current_value__sum"
        ]
        xirr = sum(list(map(float, investments.values_list("xirr", flat=True))))

        res = {
            "investments": FundInvestmentSerializer(investments, many=True).data,
            "total_amount_invested": total_amount_invested,
            "current_value": current_value,
            "returns": current_value - total_amount_invested,
            "p_returns": (
                (current_value - total_amount_invested) / total_amount_invested
            )
            * 100,
            "xirr": xirr / len(investments),
        }
        return Response(res, status=status.HTTP_200_OK)

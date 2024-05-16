from _decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from datahub.serializers import SecuritySerializer, SecurityListSerializer
from user_investment.models import Investment


class InvestmentSerializer(serializers.ModelSerializer):
    security = SecurityListSerializer(read_only=True)
    avg_price = serializers.SerializerMethodField()

    class Meta:
        model = Investment
        fields = "__all__"

    def get_avg_price(self, investment):
        return Decimal(investment.avg_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

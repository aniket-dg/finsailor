from rest_framework import serializers

from datahub.serializers import SecuritySerializer, SecurityListSerializer
from user_investment.models import Investment


class InvestmentSerializer(serializers.ModelSerializer):
    security = SecurityListSerializer(read_only=True)

    class Meta:
        model = Investment
        fields = "__all__"

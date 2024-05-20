from rest_framework import serializers

from mutual_funds.models import FundInvestment


class FundInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundInvestment
        fields = "__all__"

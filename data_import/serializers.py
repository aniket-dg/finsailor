from rest_framework import serializers

from data_import.models import TradeBook, InvestmentBook


class TradeBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeBook
        fields = "__all__"


class InvestmentBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentBook
        fields = "__all__"

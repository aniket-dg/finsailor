from _decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from data_import.models import TradeBook, InvestmentBook, MutualFundBook


class TradeBookSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = TradeBook
        fields = "__all__"

    def get_total(self, trade_book):
        if trade_book.total:
            return abs(float(trade_book.total))
        return float(trade_book.quantity) * float(trade_book.net_rate)


class InvestmentBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentBook
        fields = "__all__"


class MutualFundBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = MutualFundBook
        fields = "__all__"

import logging
from _decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from datahub.models import Security, GeneralInfo, StockIndex
from news.serializers import StockEventSerializerForSecurity


class SecuritySerializer(serializers.ModelSerializer):
    events = StockEventSerializerForSecurity(many=True, read_only=True)

    class Meta:
        model = Security
        fields = "__all__"


logger = logging.Logger("UserInvestment - Serializers")


class SecuritySerializerForSectorWisePortfolio(serializers.ModelSerializer):
    broker = serializers.SerializerMethodField()

    class Meta:
        model = Security
        fields = ["name", "symbol", "broker"]

    def get_broker(self, security):
        return self.context.get("broker")


class SecurityListSerializer(serializers.ModelSerializer):
    last_updated_price = serializers.SerializerMethodField()

    def get_last_updated_price(self, security):
        return Decimal(security.last_updated_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    class Meta:
        model = Security
        fields = [
            "id",
            "name",
            "symbol",
            "last_updated_price",
            "price_modified_datetime",
        ]


class UpdateSecuritySerializer(serializers.Serializer):
    headers = serializers.JSONField()


class SecurityFilterSerializer(UpdateSecuritySerializer):
    symbol = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    id = serializers.CharField(required=False)


class HistoricalPricesForSecurity(serializers.Serializer):
    from_year = serializers.IntegerField(required=False)


class GeneralInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralInfo
        fields = "__all__"


class StockIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockIndex
        fields = "__all__"

import datetime
import logging
from _decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from core.serializers import InvestmentInfoSerializer
from datahub.models import Security, GeneralInfo, StockIndex, CorporateAction
from news.serializers import StockEventSerializerForSecurity


class SecuritySerializer(serializers.ModelSerializer):
    events = StockEventSerializerForSecurity(many=True, read_only=True)

    class Meta:
        model = Security
        fields = "__all__"


class SecurityCorporateActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateAction
        fields = "__all__"


class SecurityNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, security):
        return f"{security.name} ({security.symbol})"

    class Meta:
        model = Security
        fields = ["id", "name"]


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


class SecurityHistoricalPriceFilterSerializer(serializers.Serializer):
    from_date = serializers.DateField(required=True)

    def validate_from_date(self, value):
        today = datetime.datetime.now().date()

        # Check if from_date is greater than today
        if value > today:
            raise serializers.ValidationError(
                "from_date must be less than or equal to today."
            )

        return value


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

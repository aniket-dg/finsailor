import datetime
import logging
from _decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from core.serializers import InvestmentInfoSerializer
from datahub.models import Security, GeneralInfo, StockIndex, CorporateAction, CorporateActionTypeEnum
from news.serializers import StockEventSerializerForSecurity



class SecurityCorporateActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateAction
        fields = "__all__"


class SecuritySerializer(serializers.ModelSerializer):
    events = StockEventSerializerForSecurity(many=True, read_only=True)
    corporate_actions = serializers.SerializerMethodField()

    class Meta:
        model = Security
        # fields = "__all__"
        exclude = ["historical_price_info"]

    def get_corporate_actions(self, security):
        corporate_actions = security.corporate_actions.order_by('-ex_date')
        return SecurityCorporateActionSerializer(corporate_actions, many=True).data


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


class HistoricalPricesForSecuritySerializer(serializers.Serializer):
    from_year = serializers.IntegerField(required=False)



class CorporateActionFilterForSecurity(serializers.Serializer):
    CORPORATE_ACTION_TYPE = [(field.name, field.value) for field in CorporateActionTypeEnum]
    corporate_action_type = serializers.ChoiceField(choices=CORPORATE_ACTION_TYPE, required=False)
    ex_date = serializers.DateField(required=False)
    ex_date__gte = serializers.DateField(required=False)


class GeneralInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralInfo
        fields = "__all__"


class StockIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockIndex
        fields = "__all__"

from rest_framework import serializers

from datahub.models import Security, GeneralInfo, StockIndex
from news.serializers import StockEventSerializerForSecurity


class SecuritySerializer(serializers.ModelSerializer):
    events = StockEventSerializerForSecurity(many=True, read_only=True)

    class Meta:
        model = Security
        fields = "__all__"


class SecuritySerializerForSectorWisePortfolio(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = ["name", "symbol"]


class SecurityListSerializer(serializers.ModelSerializer):
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

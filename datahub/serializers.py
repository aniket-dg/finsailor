from rest_framework import serializers

from datahub.models import Security


class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = "__all__"


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

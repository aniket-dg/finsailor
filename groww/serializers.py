from rest_framework import serializers

from groww.models import GrowwRequestHeader


class GrowwRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrowwRequestHeader
        fields = "__all__"


class SchemeSearchSerializer(serializers.Serializer):
    isin = serializers.CharField(max_length=100)
    scheme_type = serializers.CharField(max_length=100)

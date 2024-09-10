from rest_framework import serializers

from groww.models import GrowwRequestHeader


class GrowwRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrowwRequestHeader
        fields = "__all__"


class GrowwRequestGETSerializer(serializers.ModelSerializer):
    headers = serializers.CharField()

    class Meta:
        model = GrowwRequestHeader
        fields = "__all__"


class SchemeSearchSerializer(serializers.Serializer):
    search_id = serializers.CharField(max_length=500)


class SchemeTransactionSerializer(serializers.Serializer):
    folio_number = serializers.CharField(max_length=500)
    scheme_code = serializers.CharField(max_length=500)
    page = serializers.IntegerField(required=False)
    size = serializers.IntegerField(required=False)

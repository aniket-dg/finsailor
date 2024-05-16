from rest_framework import serializers


class SecuritySymbolSerializer(serializers.Serializer):
    symbol = serializers.CharField()

from rest_framework import serializers

from news.models import StockEvent


class StockEventSerializerForSecurity(serializers.ModelSerializer):
    class Meta:
        model = StockEvent
        fields = ["purpose", "details", "date"]

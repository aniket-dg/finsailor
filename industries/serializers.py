from rest_framework import serializers

from industries.models import MacroSector


class MacroSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MacroSector
        fields = "__all__"

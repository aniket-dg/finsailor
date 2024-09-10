from rest_framework import serializers

from mutual_funds.models import *


class FundSecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = FundSecurity
        fields = "__all__"


class FundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fund
        fields = "__all__"


class FundListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fund
        fields = ["id", "scheme_name", "description"]


class FundTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundTransaction
        fields = "__all__"


class SIPDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SIPDetails
        fields = "__all__"


class FundInvestmentFolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundInvestmentFolio
        fields = "__all__"


class FundInvestmentSerializer(serializers.ModelSerializer):
    fund = FundListSerializer()
    folios = FundInvestmentFolioSerializer(many=True)
    transactions = FundTransactionSerializer(many=True)

    class Meta:
        model = FundInvestment
        fields = "__all__"

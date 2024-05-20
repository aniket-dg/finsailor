from _decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from datahub.serializers import SecuritySerializer, SecurityListSerializer
from user_investment.models import Investment
from user_investment.utils import get_security_percentage_change


class InvestmentSerializer(serializers.ModelSerializer):
    security = SecurityListSerializer(read_only=True)
    avg_price = serializers.SerializerMethodField()
    change = serializers.SerializerMethodField()
    returns = serializers.SerializerMethodField()
    amount_invested = serializers.SerializerMethodField()

    class Meta:
        model = Investment
        fields = [
            "security",
            "avg_price",
            "change",
            "quantity",
            "buying_prices",
            "selling_prices",
            "user",
            "returns",
            "amount_invested",
        ]

    def get_amount_invested(self, investment):
        return Decimal(investment.quantity * investment.avg_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def get_returns(self, investment):
        invested_value = investment.quantity * investment.avg_price
        current_value = investment.security.last_updated_price * investment.quantity
        returns = current_value - invested_value
        res = {
            "current_value": Decimal(current_value).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            "change": Decimal(returns).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            "p_change": Decimal((returns / invested_value) * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
        }
        return res

    def get_avg_price(self, investment):
        return Decimal(investment.avg_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def get_change(self, investment):
        return get_security_percentage_change(investment)

import json
from _decimal import Decimal, ROUND_HALF_UP

from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from data_import.models import TradeBook
from datahub.models import Security
from users.models import User


class BrokerInvestment(models.Model):
    security = models.ForeignKey(
        Security, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity = models.IntegerField(default=0)
    avg_price = models.DecimalField(
        decimal_places=4, null=True, blank=True, max_digits=12
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    broker = models.CharField(max_length=100, default="Groww")
    execution_datetime = models.DateTimeField(null=True, blank=True)
    trade_book = models.ForeignKey(
        TradeBook,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="broker_investment",
    )


class Investment(models.Model):
    security = models.ForeignKey(
        Security,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="investments",
    )
    quantity = models.IntegerField(default=0)
    avg_price = models.DecimalField(
        decimal_places=4, null=True, blank=True, max_digits=12
    )
    buying_prices = ArrayField(models.JSONField(default=dict), default=list)
    selling_prices = ArrayField(models.JSONField(default=dict), default=list)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    broker_investments = models.ManyToManyField(
        BrokerInvestment, related_name="investments", blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["security", "user"], name="unique_security_user"
            )
        ]

    def get_broker_investments(self, broker):
        if broker.lower() == "groww":
            investments = self.broker_investments.filter(broker="Groww")
        elif broker.lower() == "zerodha":
            investments = self.broker_investments.filter(broker="Zerodha")
        else:
            investments = self.broker_investments.all()

        return investments

    def calculate_amount_invested(self, broker):
        broker_investments = self.get_broker_investments(broker)
        old_quantity = 0
        old_avg_price = 0

        for investment in broker_investments:
            trade_book = investment.trade_book
            if trade_book.buy_sell.lower() in ["b", "buy"]:
                new_quantity = trade_book.quantity
                net_rate = Decimal(trade_book.net_rate)
                rounded_net_rate = net_rate.quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                new_avg_price = abs(rounded_net_rate)
                new_cost = new_avg_price * new_quantity
                old_cost = old_avg_price * old_quantity
                avg_price = (new_cost + old_cost) / (old_quantity + new_quantity)
                old_avg_price = avg_price
                old_quantity = old_quantity + trade_book.quantity
            else:
                old_quantity = old_quantity - abs(trade_book.quantity)

        return old_quantity * old_avg_price

    def calculate_current_value(self, broker):
        broker_investments = self.get_broker_investments(broker)
        quantities = sum(broker_investments.values_list("quantity", flat=True))
        current_value = self.security.last_updated_price * quantities

        return current_value

    def calculate_avg_prices(self, broker):
        broker_investments = self.get_broker_investments(broker)

    def calculate_quantities(self, broker):
        broker_investments = self.get_broker_investments(broker)
        return sum(broker_investments.values_list("quantity", flat=True))


def get_amount_invested(investment, broker):
    broker_investment = investment.get_broker_investments(broker)
    user_investment = investment
    user_investment.avg_price = Decimal("0.0")
    user_investment.quantity = 0
    user_investment.buying_prices = []
    user_investment.selling_prices = []

    for b_investment in broker_investment:
        trade_book = b_investment.trade_book
        old_quantity = user_investment.quantity
        old_avg_price = user_investment.avg_price

        if trade_book.buy_sell.lower() in ["b", "buy"]:
            new_quantity = trade_book.quantity
            net_rate = Decimal(trade_book.net_rate)
            rounded_net_rate = net_rate.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            new_avg_price = abs(rounded_net_rate)
            new_cost = new_avg_price * new_quantity
            old_cost = old_avg_price * old_quantity

            # Calculate new average price
            total_quantity = old_quantity + new_quantity
            if total_quantity > 0:
                avg_price = (old_cost + new_cost) / total_quantity
            else:
                avg_price = Decimal("0.0")

            user_investment.avg_price = avg_price
            user_investment.buying_prices.append(
                {"net_rate": trade_book.net_rate, "quantity": trade_book.quantity}
            )

            # Update the total quantity
            user_investment.quantity = total_quantity

        elif trade_book.buy_sell.lower() in ["s", "sell"]:
            sell_quantity = abs(trade_book.quantity)

            # Ensure quantity does not go negative
            if old_quantity >= sell_quantity:
                user_investment.quantity = old_quantity - sell_quantity
                user_investment.selling_prices.append(
                    {"net_rate": trade_book.net_rate, "quantity": trade_book.quantity}
                )
            else:
                raise ValueError("Sell quantity exceeds the available quantity")

    return user_investment.quantity, user_investment.avg_price

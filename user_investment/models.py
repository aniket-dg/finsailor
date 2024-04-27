from django.contrib.postgres.fields import ArrayField
from django.db import models

from datahub.models import Security
from users.models import User


class Investment(models.Model):
    security = models.ForeignKey(
        Security, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity = models.IntegerField(default=0)
    avg_price = models.DecimalField(
        decimal_places=2, null=True, blank=True, max_digits=6
    )
    buying_prices = ArrayField(
        models.DecimalField(decimal_places=2, max_digits=6), default=list
    )
    selling_prices = ArrayField(
        models.DecimalField(decimal_places=2, max_digits=6), default=list
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["security", "user"], name="unique_security_user"
            )
        ]

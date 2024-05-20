from django.contrib.postgres.fields import ArrayField
from django.db import models

from datahub.models import CustomJSONEncoder
from users.models import User


class Fund(models.Model):
    scheme_name = models.CharField(max_length=100)
    nav = models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True)
    nav_date = models.DateField(null=True, blank=True)
    additional_data = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )

    def __str__(self):
        return f"{self.scheme_name}"


class FundInvestment(models.Model):
    fund = models.ForeignKey(
        Fund,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="investments",
    )
    avg_nav = models.DecimalField(
        blank=True, decimal_places=5, max_digits=10, null=True
    )
    units = models.DecimalField(decimal_places=5, max_digits=10, default=0)

    units_purchased = ArrayField(
        models.DecimalField(decimal_places=5, max_digits=10, default=0), default=list
    )
    nav_purchased = ArrayField(
        models.DecimalField(decimal_places=5, max_digits=10, default=0), default=list
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f""

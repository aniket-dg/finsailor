from datetime import datetime

from django.contrib.postgres.fields import ArrayField
from django.db import models

from datahub.models import CustomJSONEncoder
from users.models import User


class Fund(models.Model):
    scheme_code = models.CharField(max_length=255)
    folio_number = models.CharField(max_length=255)
    units = models.FloatField()
    calculate_amount_invested = models.FloatField()
    average_nav = models.FloatField()
    current_nav = models.FloatField()
    current_nav_date = models.DateTimeField()
    xirr = models.FloatField()
    source = models.CharField(max_length=255)
    folio_type = models.CharField(max_length=1)
    scheme_name = models.CharField(max_length=255)
    search_id = models.CharField(max_length=255)
    isin = models.CharField(max_length=255)
    scheme_type = models.CharField(max_length=255)
    day_change = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    sip_details = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    plan_type = models.CharField(max_length=255)
    scheme_config = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    folios = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    has_multiple_folio = models.BooleanField()
    calculate_current_value = models.FloatField()

    def __str__(self):
        return f"{self.scheme_name}"

    @classmethod
    def create_from_dict(cls, data):
        # Convert currentNavDate to a datetime object
        current_nav_date = datetime.strptime(
            data["currentNavDate"], "%Y-%m-%dT00:00:00"
        )

        # Create and return the model instance
        return cls.objects.create(
            scheme_code=data["schemeCode"],
            folio_number=data["folioNumber"],
            units=data["units"],
            calculate_amount_invested=data["amountInvested"],
            average_nav=data["averageNav"],
            current_nav=data["currentNav"],
            current_nav_date=current_nav_date,
            xirr=data["xirr"],
            source=data["source"],
            folio_type=data["folioType"],
            scheme_name=data["schemeName"],
            search_id=data["searchId"],
            isin=data["isin"],
            scheme_type=data["schemeType"],
            day_change=data["dayChange"],
            sip_details=data["sipDetails"],
            plan_type=data["planType"],
            scheme_config=data["schemeConfig"],
            folios=data["folios"],
            has_multiple_folio=data["hasMultipleFolio"],
            calculate_current_value=data["currentValue"],
        )


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

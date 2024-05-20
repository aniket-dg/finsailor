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

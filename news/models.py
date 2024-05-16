from django.db import models

from datahub.models import Security


# Create your models here.
class StockEvent(models.Model):
    company = models.CharField(max_length=500)
    security = models.ForeignKey(
        Security,
        null=True,
        blank=True,
        related_name="events",
        on_delete=models.SET_NULL,
    )
    purpose = models.CharField(max_length=100)
    details = models.TextField(null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.company} - {self.purpose}"

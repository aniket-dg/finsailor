from django.db import models


# Create your models here.
class TradeBook(models.Model):
    order_no = models.CharField(unique=True, max_length=100)
    order_time = models.TimeField(null=True, blank=True)
    trade_time = models.TimeField(null=True, blank=True)

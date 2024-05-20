from django.db import models

from users.models import User


class HTTP_METHOD(models.TextChoices):
    """Choices for the crop type - related to succession farming.

    * PRIMARY_WITH_SUCCESSION = Primary crop, with a secondary crop allowed
    * PRIMARY_NO_SUCCESSION   = Primary crop, no secondary crop allowed
    * SECONDARY               = Secondary crop
    * ADDITIONAL              = Additional (or "extra") crop, such as "beheersgras",
                                which results in "beheershooi" (HAY) as comp. fodder.
    """

    GET = "get", "GET"
    POST = "post", "POST"
    PATCH = "patch", "PATCH"
    PUT = "put", "PUT"


class GrowwRequestHeader(models.Model):
    headers = models.JSONField()
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    method = models.CharField(choices=HTTP_METHOD.choices, default=HTTP_METHOD.GET)

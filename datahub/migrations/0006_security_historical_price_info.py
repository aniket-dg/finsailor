# Generated by Django 5.0.4 on 2024-04-23 12:31

import datahub.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datahub", "0005_alter_security_last_updated_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="security",
            name="historical_price_info",
            field=models.JSONField(
                default=dict, encoder=datahub.models.CustomJSONEncoder
            ),
        ),
    ]
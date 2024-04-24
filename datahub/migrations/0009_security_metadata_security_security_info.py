# Generated by Django 5.0.4 on 2024-04-24 07:55

import datahub.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datahub", "0008_security_basic_industry"),
    ]

    operations = [
        migrations.AddField(
            model_name="security",
            name="metadata",
            field=models.JSONField(
                default=dict, encoder=datahub.models.CustomJSONEncoder
            ),
        ),
        migrations.AddField(
            model_name="security",
            name="security_info",
            field=models.JSONField(
                default=dict, encoder=datahub.models.CustomJSONEncoder
            ),
        ),
    ]

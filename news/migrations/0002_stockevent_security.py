# Generated by Django 5.0.4 on 2024-05-15 19:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datahub", "0035_remove_security_event"),
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="stockevent",
            name="security",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="events",
                to="datahub.security",
            ),
        ),
    ]

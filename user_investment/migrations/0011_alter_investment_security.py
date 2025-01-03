# Generated by Django 5.0.4 on 2024-05-21 10:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datahub", "0035_remove_security_event"),
        ("user_investment", "0010_remove_brokerinvestment_buying_prices_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="investment",
            name="security",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="investments",
                to="datahub.security",
            ),
        ),
    ]

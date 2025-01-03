# Generated by Django 5.0.4 on 2024-10-09 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datahub", "0045_watchlist"),
    ]

    operations = [
        migrations.AlterField(
            model_name="corporateaction",
            name="corporate_action_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Dividend", "dividend"),
                    ("Annual General Meeting", "agm"),
                    ("BuyBack", "buyback"),
                ],
                max_length=100,
                null=True,
            ),
        ),
    ]

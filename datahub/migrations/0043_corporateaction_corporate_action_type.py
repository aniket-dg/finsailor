# Generated by Django 5.0.4 on 2024-09-30 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datahub", "0042_corporateaction"),
    ]

    operations = [
        migrations.AddField(
            model_name="corporateaction",
            name="corporate_action_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("dividend", "Dividend"),
                    ("agm", "Annual General Meeting"),
                    ("buyback", "BuyBack"),
                ],
                max_length=100,
                null=True,
            ),
        ),
    ]

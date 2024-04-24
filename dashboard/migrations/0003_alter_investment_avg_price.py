# Generated by Django 5.0.4 on 2024-04-23 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0002_investment_user_investment_unique_security_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="investment",
            name="avg_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=6, null=True
            ),
        ),
    ]

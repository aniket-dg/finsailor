# Generated by Django 5.0.4 on 2024-08-22 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_investment", "0017_remove_investment_buying_prices_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="investment",
            name="broker",
            field=models.CharField(
                choices=[("groww", "Groww"), ("zerodha", "Zerodha")], default="groww"
            ),
        ),
    ]

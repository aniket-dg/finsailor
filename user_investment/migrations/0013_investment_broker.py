# Generated by Django 5.0.4 on 2024-05-23 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_investment", "0012_brokerinvestment_trade_book"),
    ]

    operations = [
        migrations.AddField(
            model_name="investment",
            name="broker",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

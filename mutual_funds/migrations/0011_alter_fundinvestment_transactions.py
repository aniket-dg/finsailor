# Generated by Django 5.0.4 on 2024-05-25 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mutual_funds", "0010_fundinvestment_transactions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fundinvestment",
            name="transactions",
            field=models.ManyToManyField(
                related_name="fund_investments", to="mutual_funds.fundtransaction"
            ),
        ),
    ]
# Generated by Django 5.0.4 on 2024-08-22 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user_investment", "0018_alter_investment_broker"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Transactions",
            new_name="StockTransactions",
        ),
    ]

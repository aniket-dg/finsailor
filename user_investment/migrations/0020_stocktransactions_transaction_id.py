# Generated by Django 5.0.4 on 2024-08-22 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_investment", "0019_rename_transactions_stocktransactions"),
    ]

    operations = [
        migrations.AddField(
            model_name="stocktransactions",
            name="transaction_id",
            field=models.CharField(default=1, unique=True),
            preserve_default=False,
        ),
    ]

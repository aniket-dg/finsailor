# Generated by Django 5.0.4 on 2024-04-24 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_import", "0012_alter_tradebook_buy_sell"),
    ]

    operations = [
        migrations.AddField(
            model_name="tradebook",
            name="broker",
            field=models.CharField(default="Groww", max_length=100),
        ),
    ]

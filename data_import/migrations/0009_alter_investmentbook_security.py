# Generated by Django 5.0.4 on 2024-04-24 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_import", "0008_alter_tradebook_exchange_alter_tradebook_security"),
    ]

    operations = [
        migrations.AlterField(
            model_name="investmentbook",
            name="security",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

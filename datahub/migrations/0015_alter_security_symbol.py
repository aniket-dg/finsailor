# Generated by Django 5.0.4 on 2024-04-24 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datahub", "0014_alter_security_symbol"),
    ]

    operations = [
        migrations.AlterField(
            model_name="security",
            name="symbol",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]

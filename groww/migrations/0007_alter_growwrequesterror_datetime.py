# Generated by Django 5.0.4 on 2024-09-09 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("groww", "0006_growwrequesterror"),
    ]

    operations = [
        migrations.AlterField(
            model_name="growwrequesterror",
            name="datetime",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

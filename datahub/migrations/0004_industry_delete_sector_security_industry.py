# Generated by Django 5.0.4 on 2024-04-23 12:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datahub", "0003_security_scrip_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="Industry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("macro", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "basic_industry",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="Sector",
        ),
        migrations.AddField(
            model_name="security",
            name="industry",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="datahub.industry",
            ),
        ),
    ]
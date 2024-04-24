# Generated by Django 5.0.4 on 2024-04-19 18:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("datahub", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UploadedPDF",
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
                ("pdf_file", models.FileField(upload_to="pdf_files/")),
                ("processed", models.BooleanField(default=False)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="TradeBook",
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
                ("order_no", models.CharField(max_length=100, unique=True)),
                ("order_time", models.TimeField(blank=True, null=True)),
                ("trade_time", models.TimeField(blank=True, null=True)),
                (
                    "buy_sell",
                    models.CharField(
                        choices=[("B", "Buy"), ("S", "Sell")],
                        default="B",
                        max_length=10,
                    ),
                ),
                ("quantity", models.IntegerField(default=0)),
                ("gross_rate", models.CharField(blank=True, max_length=20, null=True)),
                ("brokerage", models.CharField(blank=True, max_length=20, null=True)),
                ("net_rate", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "closing_rate",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("total", models.CharField(blank=True, max_length=20, null=True)),
                ("remarks", models.CharField(blank=True, max_length=100, null=True)),
                ("processed", models.BooleanField(default=False)),
                (
                    "exchange",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="datahub.exchange",
                    ),
                ),
                (
                    "security",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="datahub.security",
                    ),
                ),
            ],
        ),
    ]

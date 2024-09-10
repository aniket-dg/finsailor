# Generated by Django 5.0.4 on 2024-05-20 12:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_import", "0019_uploadedcontractnotepdf_user_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UploadedMutualFundReport",
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
                ("excel_file", models.FileField(upload_to="excel_files/mutual_funds/")),
                (
                    "broker",
                    models.CharField(
                        blank=True,
                        choices=[("groww", "Groww"), ("zerodha", "Zerodha")],
                        max_length=100,
                        null=True,
                    ),
                ),
                ("processed", models.BooleanField(default=False)),
                ("date", models.DateField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="uploaded_mutual_fund_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

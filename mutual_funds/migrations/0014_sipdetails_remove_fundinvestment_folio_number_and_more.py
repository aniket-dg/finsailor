# Generated by Django 5.0.4 on 2024-05-25 18:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mutual_funds", "0013_alter_fundinvestment_folio_number"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SIPDetails",
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
                ("has_active_sip", models.BooleanField()),
                ("active_sip_count", models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name="fundinvestment",
            name="folio_number",
        ),
        migrations.CreateModel(
            name="FundInvestmentFolio",
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
                ("folio_number", models.CharField(max_length=255)),
                ("units", models.FloatField()),
                ("amount_invested", models.FloatField()),
                ("average_nav", models.FloatField()),
                ("current_nav_date", models.DateField()),
                ("xirr", models.FloatField(blank=True, null=True)),
                ("portfolio_source", models.CharField(max_length=255)),
                ("folio_type", models.CharField(max_length=1)),
                (
                    "first_unrealised_purchase_date",
                    models.DateField(blank=True, null=True),
                ),
                ("current_value", models.FloatField()),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fund_investment_folios",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sip_details",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mutual_funds.sipdetails",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="fundinvestment",
            name="folios",
            field=models.ManyToManyField(
                blank=True,
                related_name="fund_investments",
                to="mutual_funds.fundinvestmentfolio",
            ),
        ),
    ]

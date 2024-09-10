# Generated by Django 5.0.4 on 2024-05-10 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="StockIndex",
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
                ("key", models.CharField(max_length=100)),
                ("index", models.CharField(max_length=100)),
                ("indexSymbol", models.CharField(max_length=100)),
                ("last", models.FloatField(blank=True, null=True)),
                ("variation", models.FloatField()),
                ("percentChange", models.FloatField()),
                ("open", models.FloatField()),
                ("high", models.FloatField()),
                ("low", models.FloatField()),
                ("previousClose", models.FloatField()),
                ("yearHigh", models.FloatField()),
                ("yearLow", models.FloatField()),
                ("indicativeClose", models.FloatField()),
                ("pe", models.CharField(max_length=10)),
                ("pb", models.CharField(max_length=10)),
                ("dy", models.CharField(max_length=10)),
                ("declines", models.CharField(max_length=10)),
                ("advances", models.CharField(max_length=10)),
                ("unchanged", models.CharField(max_length=10)),
                ("perChange365d", models.FloatField()),
                ("date365dAgo", models.CharField(max_length=20)),
                ("chart365dPath", models.URLField()),
                ("date30dAgo", models.CharField(max_length=20)),
                ("perChange30d", models.FloatField()),
                ("chart30dPath", models.URLField()),
                ("chartTodayPath", models.URLField()),
                ("previousDay", models.FloatField()),
                ("oneWeekAgo", models.FloatField()),
                ("oneMonthAgo", models.FloatField()),
                ("oneYearAgo", models.FloatField()),
            ],
        ),
    ]

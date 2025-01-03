# Generated by Django 5.0.4 on 2024-05-10 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "datahub",
            "0023_rename_data_365_day_ago_todaystockindex_date_365_day_ago_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="stockindex",
            name="advances",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="chart30dPath",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="chart365dPath",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="chartTodayPath",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="date30dAgo",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="date365dAgo",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="declines",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="dy",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="high",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="indicativeClose",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="low",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="oneMonthAgo",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="oneWeekAgo",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="oneYearAgo",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="open",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="pb",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="pe",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="perChange30d",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="perChange365d",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="percentChange",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="previousClose",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="previousDay",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="unchanged",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="variation",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="yearHigh",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stockindex",
            name="yearLow",
            field=models.FloatField(blank=True, null=True),
        ),
    ]

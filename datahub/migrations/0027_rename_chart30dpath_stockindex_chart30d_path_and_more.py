# Generated by Django 5.0.4 on 2024-05-10 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("datahub", "0026_alter_stockindex_advances_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="stockindex",
            old_name="chart30dPath",
            new_name="chart30d_path",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="chart365dPath",
            new_name="chart365d_path",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="chartTodayPath",
            new_name="chart_today_path",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="date30dAgo",
            new_name="date30d_ago",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="date365dAgo",
            new_name="date365d_ago",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="indexSymbol",
            new_name="index_symbol",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="indicativeClose",
            new_name="indicative_close",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="oneMonthAgo",
            new_name="one_month_ago",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="oneWeekAgo",
            new_name="one_week_ago",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="oneYearAgo",
            new_name="one_year_ago",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="perChange30d",
            new_name="per_change30d",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="perChange365d",
            new_name="per_change365d",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="percentChange",
            new_name="percent_change",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="previousClose",
            new_name="previous_close",
        ),
        migrations.RenameField(
            model_name="stockindex",
            old_name="previousDay",
            new_name="previous_day",
        ),
    ]

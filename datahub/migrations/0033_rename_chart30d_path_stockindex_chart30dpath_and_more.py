# Generated by Django 5.0.4 on 2024-05-15 12:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datahub', '0032_rename_yearhigh_stockindex_year_high_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockindex',
            old_name='chart30d_path',
            new_name='chart30dPath',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='chart365d_path',
            new_name='chart365dPath',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='chart_today_path',
            new_name='chartTodayPath',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='date30d_ago',
            new_name='date30dAgo',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='date365d_ago',
            new_name='date365dAgo',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='index_symbol',
            new_name='indexSymbol',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='indicative_close',
            new_name='indicativeClose',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='one_month_ago',
            new_name='oneMonthAgo',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='one_week_ago',
            new_name='oneWeekAgo',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='one_year_ago',
            new_name='oneYearAgo',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='per_change30d',
            new_name='perChange30d',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='per_change365d',
            new_name='perChange365d',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='percent_change',
            new_name='percentChange',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='previous_close',
            new_name='previousClose',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='previous_day',
            new_name='previousDay',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='year_high',
            new_name='yearHigh',
        ),
        migrations.RenameField(
            model_name='stockindex',
            old_name='year_low',
            new_name='yearLow',
        ),
    ]
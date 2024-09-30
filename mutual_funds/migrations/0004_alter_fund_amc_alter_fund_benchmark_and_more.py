# Generated by Django 5.0.4 on 2024-05-25 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mutual_funds", "0003_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fund",
            name="amc",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="benchmark",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="benchmark_name",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="direct_scheme_code",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="dividend",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="exit_load",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="expense_ratio",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="fund_house",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="fund_manager",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="groww_scheme_code",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="isin",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="meta_title",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="nav_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="prod_code",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="rta_scheme_code",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="scheme_code",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="scheme_name",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="sub_sub_category",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="super_category",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="fund",
            name="swp_frequencies",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="unique_groww_scheme_code",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fundsecurity",
            name="market_cap",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fundsecurity",
            name="nature_name",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fundsecurity",
            name="rating_market_cap",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fundsecurity",
            name="scheme_code",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
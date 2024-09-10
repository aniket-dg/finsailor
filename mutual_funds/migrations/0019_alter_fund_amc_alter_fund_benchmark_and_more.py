# Generated by Django 5.0.4 on 2024-09-09 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mutual_funds", "0018_fund_five_year_returns_fund_one_year_returns_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fund",
            name="amc",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="benchmark",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="benchmark_name",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="category",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="exit_load",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="expense_ratio",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="fund_house",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="fund_manager",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="groww_scheme_code",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="isin",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="meta_desc",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="meta_robots",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="meta_title",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="plan_type",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="prod_code",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="registrar_agent",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="rta_scheme_code",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="scheme_code",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="scheme_name",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="scheme_type",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="search_id",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="stamp_duty",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="sub_category",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="fund",
            name="super_category",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]

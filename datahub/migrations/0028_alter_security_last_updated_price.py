# Generated by Django 5.0.4 on 2024-05-10 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datahub", "0027_rename_chart30dpath_stockindex_chart30d_path_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="security",
            name="last_updated_price",
            field=models.DecimalField(
                blank=True, decimal_places=5, max_digits=10, null=True
            ),
        ),
    ]

# Generated by Django 5.0.4 on 2024-04-24 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("industries", "0002_rename_sector_basicindustry_industry"),
    ]

    operations = [
        migrations.AlterField(
            model_name="basicindustry",
            name="basic_ind_code",
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]

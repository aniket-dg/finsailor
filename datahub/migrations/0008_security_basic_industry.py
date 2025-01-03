# Generated by Django 5.0.4 on 2024-04-24 07:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datahub", "0007_remove_security_industry_delete_industry"),
        ("industries", "0003_alter_basicindustry_basic_ind_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="security",
            name="basic_industry",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="industries.basicindustry",
            ),
        ),
    ]

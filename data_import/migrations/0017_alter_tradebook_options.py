# Generated by Django 5.0.4 on 2024-05-01 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("data_import", "0016_remove_uploadedcontractnotepdf_date_created_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tradebook",
            options={"ordering": ["execution_datetime"]},
        ),
    ]

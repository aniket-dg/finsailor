# Generated by Django 5.0.4 on 2024-04-24 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_import", "0015_alter_uploadedcontractnotepdf_broker_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="uploadedcontractnotepdf",
            name="date_created",
        ),
        migrations.RemoveField(
            model_name="uploadeddematreportpdf",
            name="date_created",
        ),
        migrations.AddField(
            model_name="uploadedcontractnotepdf",
            name="date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="uploadeddematreportpdf",
            name="date",
            field=models.DateField(blank=True, null=True),
        ),
    ]

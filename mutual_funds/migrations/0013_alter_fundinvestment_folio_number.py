# Generated by Django 5.0.4 on 2024-05-25 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mutual_funds", "0012_alter_fundtransaction_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fundinvestment",
            name="folio_number",
            field=models.CharField(blank=True, max_length=500, null=True, unique=True),
        ),
    ]

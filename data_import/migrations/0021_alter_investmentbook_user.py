# Generated by Django 5.0.4 on 2024-05-20 12:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_import", "0020_uploadedmutualfundreport"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="investmentbook",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="uploaded_investment_books",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]

# Generated by Django 5.0.4 on 2024-05-15 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_import', '0017_alter_tradebook_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradebook',
            name='order_no',
            field=models.CharField(max_length=100),
        ),
    ]

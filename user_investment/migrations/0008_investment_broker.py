# Generated by Django 5.0.4 on 2024-05-21 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_investment', '0007_alter_investment_buying_prices_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='investment',
            name='broker',
            field=models.CharField(default='Groww', max_length=100),
        ),
    ]
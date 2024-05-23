# Generated by Django 5.0.4 on 2024-05-21 10:02

import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datahub', '0035_remove_security_event'),
        ('user_investment', '0008_investment_broker'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investment',
            name='broker',
        ),
        migrations.CreateModel(
            name='BrokerInvestment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('avg_price', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('buying_prices', django.contrib.postgres.fields.ArrayField(base_field=models.JSONField(default=dict), default=list, size=None)),
                ('quantities', django.contrib.postgres.fields.ArrayField(base_field=models.JSONField(default=dict), default=list, size=None)),
                ('broker', models.CharField(default='Groww', max_length=100)),
                ('execution_datetime', models.DateTimeField(blank=True, null=True)),
                ('security', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='datahub.security')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='investment',
            name='broker_investments',
            field=models.ManyToManyField(blank=True, related_name='investments', to='user_investment.brokerinvestment'),
        ),
    ]
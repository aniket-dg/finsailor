# Generated by Django 5.0.4 on 2024-04-23 07:34

import users.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_remove_user_username"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", users.models.UserManager()),
            ],
        ),
    ]

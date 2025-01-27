# Generated by Django 4.2.4 on 2025-01-25 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_profile_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("user", "User"), ("creator", "Creator")],
                default="user",
                max_length=10,
            ),
        ),
    ]

# Generated by Django 4.2.4 on 2025-04-05 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_profile_telegram_url_profile_tiktok_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="username",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]

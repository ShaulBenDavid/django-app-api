# Generated by Django 4.2.4 on 2024-10-25 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_profile_instagram_url_profile_linkedin_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="group",
            name="is_public",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="profile",
            name="is_public",
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 4.2.4 on 2025-04-05 07:29

from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_alter_profile_username"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="profile",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("username"),
                name="unique_lower_username",
            ),
        ),
    ]

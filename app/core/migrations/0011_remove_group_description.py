# Generated by Django 4.2.4 on 2025-01-31 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_customurl"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="group",
            name="description",
        ),
    ]

# Generated by Django 4.2.4 on 2024-07-19 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_usersubscriptioncollection_last_data_sync"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="description",
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="usersubscriptioncollection",
            name="last_data_sync",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

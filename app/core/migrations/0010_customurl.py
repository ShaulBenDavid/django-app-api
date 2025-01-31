# Generated by Django 4.2.4 on 2025-01-25 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_user_role"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomURL",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("url", models.URLField(max_length=255)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="custom_urls",
                        to="core.profile",
                    ),
                ),
            ],
        ),
    ]

# Generated by Django 4.2.7 on 2023-11-26 10:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Listing",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=64)),
                ("description", models.TextField()),
                ("price", models.FloatField()),
                ("image_url", models.URLField(blank=True)),
                ("active", models.CharField(default="yes", max_length=64)),
                ("category", models.CharField(blank=True, max_length=64)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "listed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owner",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

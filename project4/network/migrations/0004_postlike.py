# Generated by Django 4.2.7 on 2023-12-07 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("network", "0003_userfollowing_delete_comment"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostLike",
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
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likedPost",
                        to="network.post",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="like",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

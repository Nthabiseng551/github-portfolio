# Generated by Django 4.2.7 on 2023-12-27 08:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("pregnancy", "0012_alter_test_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="test",
            name="done",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="test",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tests",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]

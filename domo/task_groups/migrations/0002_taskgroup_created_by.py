# Generated by Django 4.2.7 on 2023-11-21 06:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("task_groups", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskgroup",
            name="created_by",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
# Generated by Django 4.2.7 on 2023-11-22 21:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("projects", "0004_alter_project_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectJoinRequest",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("message", models.CharField(max_length=200)),
                ("created_at", models.DateTimeField()),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projects.project",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

# Generated by Django 4.2.6 on 2023-11-06 04:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("domo_api", "0005_alter_project_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserStack",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("language", models.CharField()),
                ("code_amount", models.IntegerField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GithubStatus",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("status", models.CharField()),
                ("last_update", models.DateTimeField()),
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
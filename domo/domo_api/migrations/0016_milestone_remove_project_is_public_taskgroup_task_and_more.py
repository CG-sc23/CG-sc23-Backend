# Generated by Django 4.2.7 on 2023-11-13 11:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("domo_api", "0015_remove_user_is_public"),
    ]

    operations = [
        migrations.CreateModel(
            name="Milestone",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("tags", models.JSONField(blank=True, null=True)),
                ("subject", models.CharField(max_length=100)),
                ("status", models.CharField(default="READY", max_length=20)),
                ("created_at", models.DateTimeField()),
                ("due_date", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name="project",
            name="is_public",
        ),
        migrations.CreateModel(
            name="TaskGroup",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=100)),
                ("tags", models.JSONField(blank=True, null=True)),
                ("status", models.CharField(default="READY", max_length=20)),
                ("created_at", models.DateTimeField()),
                ("due_date", models.DateTimeField(blank=True, null=True)),
                (
                    "milestone",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="domo_api.milestone",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                ("description_resource_links", models.JSONField(blank=True, null=True)),
                ("tags", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField()),
                ("is_public", models.BooleanField(default=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="domo_api.taskgroup",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="milestone",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="domo_api.project"
            ),
        ),
    ]

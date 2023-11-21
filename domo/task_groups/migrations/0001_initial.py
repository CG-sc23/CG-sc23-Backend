# Generated by Django 4.2.7 on 2023-11-21 05:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("milestones", "0002_initial"),
    ]

    operations = [
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
                        to="milestones.milestone",
                    ),
                ),
            ],
        ),
    ]

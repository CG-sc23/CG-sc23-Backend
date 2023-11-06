# Generated by Django 4.2.7 on 2023-11-06 07:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("domo_api", "0005_alter_project_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="projectmember",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="github_link",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="grade",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="like",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="pre_access_token",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="rating",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="short_description",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
# Generated by Django 4.2.7 on 2023-11-22 12:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("milestones", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="milestone",
            name="status",
            field=models.CharField(default="IN_PROGRESS", max_length=20),
        ),
    ]

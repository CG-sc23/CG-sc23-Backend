# Generated by Django 4.2.7 on 2023-11-20 13:14

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="S3ResourceReferenceCheck",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("resource_link", models.CharField(max_length=100)),
            ],
        ),
    ]
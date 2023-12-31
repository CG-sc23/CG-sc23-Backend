# Generated by Django 4.2.7 on 2023-11-29 09:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ads", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Ads",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("requester_email", models.CharField(max_length=100)),
                ("requester_name", models.CharField(max_length=10)),
                ("company_email", models.CharField(max_length=100)),
                ("company_name", models.CharField(max_length=30)),
                ("ads_purpose", models.CharField(max_length=100)),
                ("ads_file_link", models.TextField()),
                ("created_at", models.DateTimeField()),
                ("is_active", models.BooleanField(default=False)),
            ],
        ),
        migrations.DeleteModel(
            name="AdsRequest",
        ),
    ]

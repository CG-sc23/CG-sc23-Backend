# Generated by Django 4.2.6 on 2023-10-31 03:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("domo_api", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="EmailVerifyToken",
            new_name="SignUpEmailVerifyToken",
        ),
    ]
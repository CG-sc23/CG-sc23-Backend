# Generated by Django 4.2.7 on 2023-11-05 05:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("domo_api", "0002_rename_emailverifytoken_signupemailverifytoken"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_public",
            field=models.BooleanField(default=True),
        ),
    ]

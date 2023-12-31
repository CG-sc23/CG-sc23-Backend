# Generated by Django 4.2.7 on 2023-11-20 13:14

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("email", models.EmailField(max_length=320, unique=True)),
                ("name", models.CharField(max_length=20)),
                ("github_link", models.TextField(blank=True, null=True)),
                ("profile_image_link", models.TextField(blank=True, null=True)),
                (
                    "short_description",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("description", models.TextField(blank=True, null=True)),
                ("description_resource_links", models.JSONField(blank=True, null=True)),
                ("grade", models.IntegerField(default=0)),
                ("like", models.IntegerField(default=0)),
                ("rating", models.FloatField(default=0)),
                ("created_at", models.DateTimeField()),
                ("provider", models.CharField(default="our", max_length=20)),
                ("pre_access_token", models.TextField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_superuser", models.BooleanField(default=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]

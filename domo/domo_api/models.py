from datetime import datetime, timezone

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    use_in_migration = True

    def create_user(
        self,
        email,
        password,
        name,
        short_description=None,
        github_link=None,
        has_profile_image=False,
        provider="our",
    ):
        if not email:
            raise ValueError("must have email!")
        if not password:
            raise ValueError("must have password!")
        if not name:
            raise ValueError("must have name!")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            short_description=short_description,
            created_at=datetime.now(tz=timezone.utc),
            has_profile_image=has_profile_image,
            provider=provider,
        )
        if github_link:
            user.github_link = github_link

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, name):
        user = self.create_user(
            email=self.normalize_email(email),
            name=name,
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    id = models.AutoField(primary_key=True)

    email = models.EmailField(max_length=320, unique=True)

    name = models.CharField(max_length=20)

    github_link = models.CharField(max_length=100, null=True)

    has_profile_image = models.BooleanField(default=False)

    short_description = models.CharField(max_length=50, null=True)

    grade = models.IntegerField(null=True)

    like = models.IntegerField(null=True)

    rating = models.FloatField(null=True)

    created_at = models.DateTimeField()

    provider = models.CharField(max_length=20, default="our")

    pre_access_token = models.TextField(null=True)

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email


class PasswordResetToken(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    token = models.CharField(max_length=30)
    created_at = models.DateTimeField()

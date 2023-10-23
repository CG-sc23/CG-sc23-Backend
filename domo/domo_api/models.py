import binascii
import os

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from domo_base import settings


class UserManager(BaseUserManager):
    use_in_migration = True

    def create_user(self, email, password, name, short_description, description):
        if not email:
            raise ValueError("must have email!")
        if not password:
            raise ValueError("must have password!")
        if not name:
            raise ValueError("must have name!")

        user = self.create_user(
            email=self.normalize_email(email),
            name=name,
            short_description=short_description,
            description=description,
        )

    def create_superuser(self, email, password, name):
        user = self.create_user(
            email=self.normalize_email(email),
            name=name,
            password=password,
        )

        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    id = models.AutoField(primary_key=True)

    email = models.EmailField(max_length=320, unique=True)

    name = models.CharField(max_length=20)

    short_description = models.CharField(max_length=50, null=True)

    description = models.TextField(null=True)

    grade = models.IntegerField(null=True)

    like = models.IntegerField(null=True)

    rating = models.FloatField(null=True)

    created_at = models.DateTimeField()

    USERNAME_FIELD = "email"


class Token(models.Model):
    key = models.CharField("Key", max_length=40, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="auth_token",
        on_delete=models.CASCADE,
        verbose_name="User",
    )
    created = models.DateTimeField("Created", auto_now_add=True)

    class Meta:
        abstract = "rest_framework.authtoken" not in settings.INSTALLED_APPS

    def save(self, *args, **kwargs):
        if not self.key:  # self.key에 값이 없으면, 랜덤 문자열을 지정.
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

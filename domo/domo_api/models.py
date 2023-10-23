from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


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

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, name, short_description, description):
        user = self.create_user(
            email=self.normalize_email(email),
            name=name,
            short_description=short_description,
            description=description,
            password=password,
        )

        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    id = models.AutoField(primary_key=True)

    email = models.EmailField(max_length=320)

    password = models.CharField()

    name = models.CharField(max_length=20)

    short_description = models.CharField(max_length=50)

    description = models.TextField()

    grade = models.IntegerField(default=0)

    like = models.IntegerField(default=0)

    rating = models.FloatField(default=0.0)

    created_at = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    is_superuser = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

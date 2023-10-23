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

    email = models.EmailField(max_length=320)

    name = models.CharField(max_length=20)

    short_description = models.CharField(max_length=50, null=True)

    description = models.TextField(null=True)

    grade = models.IntegerField(null=True)

    like = models.IntegerField(null=True)

    rating = models.FloatField(null=True)

    created_at = models.DateTimeField()

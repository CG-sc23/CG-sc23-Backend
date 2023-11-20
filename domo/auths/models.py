from django.db import models
from users.models import User


# Create your models here.
class PasswordResetToken(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    token = models.CharField(max_length=30)
    created_at = models.DateTimeField()


class SignUpEmailVerifyToken(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=320, unique=True)
    token = models.CharField(max_length=30)
    created_at = models.DateTimeField()

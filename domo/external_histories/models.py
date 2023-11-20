from django.db import models
from users.models import User


# Create your models here.
class GithubStatus(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    status = models.CharField(max_length=20)
    last_update = models.DateTimeField()


class UserStack(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    language = models.CharField(max_length=20)
    code_amount = models.IntegerField()


class UserKeyword(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    keyword = models.CharField(max_length=50)
    count = models.IntegerField(default=0)

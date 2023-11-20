from django.db import models
from users.models import User


# Create your models here.
class S3ResourceReferenceCheck(models.Model):
    id = models.AutoField(primary_key=True)
    resource_link = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

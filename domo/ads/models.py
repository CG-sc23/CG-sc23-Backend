from django.db import models


# Create your models here.
class Ad(models.Model):
    id = models.AutoField(primary_key=True)

    requester_email = models.CharField(max_length=100)
    requester_name = models.CharField(max_length=10)

    company_email = models.CharField(max_length=100)
    company_name = models.CharField(max_length=30)

    purpose = models.CharField(max_length=100)

    site_link = models.TextField(default="")
    file_link = models.TextField()

    initial_exposure_count = models.IntegerField(null=True, blank=True)
    remaining_exposure_count = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField()

    is_active = models.BooleanField(default=False)

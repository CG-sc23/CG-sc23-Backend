from django.db import models


# Create your models here.
class AdsRequest(models.Model):
    id = models.AutoField(primary_key=True)

    requester_email = models.CharField(max_length=100)
    requester_name = models.CharField(max_length=10)

    company_email = models.CharField(max_length=100)
    company_name = models.CharField(max_length=30)

    ads_purpose = models.CharField(max_length=100)

    ads_file_link = models.TextField()

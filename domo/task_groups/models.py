from django.db import models
from milestones.models import Milestone
from users.models import User


# Create your models here.
class TaskGroup(models.Model):
    id = models.AutoField(primary_key=True)
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
    )

    title = models.CharField(max_length=100)
    tags = models.JSONField(null=True, blank=True)

    # READY, PROGRESSING, COMPLETED
    status = models.CharField(max_length=20, default="READY")

    created_at = models.DateTimeField()
    due_date = models.DateTimeField(null=True, blank=True)

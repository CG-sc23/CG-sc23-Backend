from django.db import models
from projects.models import Project
from users.models import User


# Create your models here.
class Milestone(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
    )

    tags = models.JSONField(null=True, blank=True)
    subject = models.CharField(max_length=100)

    # READY, IN_PROGRESS, COMPLETED
    status = models.CharField(max_length=20, default="READY")

    created_at = models.DateTimeField()
    due_date = models.DateTimeField(null=True, blank=True)

    def simple_info(self):
        return {"id": self.id, "subject": self.subject, "tags": self.tags}

from django.db import models
from task_groups.models import TaskGroup
from users.models import User


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    task_group = models.ForeignKey(
        TaskGroup,
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    description_resource_links = models.JSONField(null=True, blank=True)

    tags = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField()

    is_public = models.BooleanField(default=True)

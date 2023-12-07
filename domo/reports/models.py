from django.db import models
from tasks.models import Task
from users.models import User


class Report(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    feed = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "feed"],
                name="owner_feed_unique",
            ),
        ]

from django.db import models
from users.models import User


# Create your models here.
class Project(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    # IN_PROGRESS, COMPLETED, TERMINATED
    status = models.CharField(max_length=20, default="IN_PROGRESS")

    title = models.CharField(max_length=50)
    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    description_resource_links = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField()
    due_date = models.DateTimeField(null=True, blank=True)
    thumbnail_image = models.CharField(max_length=500, null=True, blank=True)

    def detail(self):
        return {
            "id": self.id,
            "owner": {
                "id": self.owner.id,
                "name": self.owner.name,
                "email": self.owner.email,
                "profile_image_link": self.owner.profile_image_link,
                "profile_image_updated_at": self.owner.profile_image_updated_at,
            },
            "status": self.status,
            "title": self.title,
            "short_description": self.short_description,
            "description": self.description,
            "description_resource_links": self.description_resource_links,
            "created_at": self.created_at,
            "due_date": self.due_date,
            "thumbnail_image": self.thumbnail_image,
        }


class ProjectInvite(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inviter")
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invitee")

    created_at = models.DateTimeField()


class ProjectMember(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    # OWNER, MANAGER, MEMBER
    role = models.CharField(max_length=20)
    created_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="project_user_unique",
            ),
        ]


class ProjectJoinRequest(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    message = models.CharField(max_length=200)
    created_at = models.DateTimeField()

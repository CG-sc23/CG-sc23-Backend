from datetime import datetime, timezone

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    use_in_migration = True

    def create_user(
        self,
        email,
        password,
        name,
        short_description=None,
        github_link=None,
        profile_image_link=None,
        provider="our",
    ):
        if not email:
            raise ValueError("must have email!")
        if not password:
            raise ValueError("must have password!")
        if not name:
            raise ValueError("must have name!")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            short_description=short_description,
            created_at=datetime.now(tz=timezone.utc),
            profile_image_link=profile_image_link,
            provider=provider,
        )
        if github_link:
            user.github_link = github_link

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, name):
        user = self.create_user(
            email=self.normalize_email(email),
            name=name,
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    id = models.AutoField(primary_key=True)

    email = models.EmailField(max_length=320, unique=True)
    name = models.CharField(max_length=20)
    github_link = models.TextField(null=True, blank=True)
    profile_image_link = models.TextField(null=True, blank=True)
    short_description = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    description_resource_links = models.JSONField(null=True, blank=True)
    grade = models.IntegerField(default=0)
    like = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    created_at = models.DateTimeField()
    provider = models.CharField(max_length=20, default="our")
    pre_access_token = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email


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


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    # READY, PROGRESSING, COMPLETED, GIVEUP
    status = models.CharField(max_length=20, default="READY")

    title = models.CharField(max_length=50)
    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    description_resource_links = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField()
    like = models.IntegerField(default=0)

    def detail(self):
        return {
            "id": self.id,
            "owner": self.owner.id,
            "status": self.status,
            "title": self.title,
            "short_description": self.short_description,
            "description": self.description,
            "description_resource_links": self.description_resource_links,
            "created_at": self.created_at,
            "like": self.like,
        }


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


class Milestone(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )

    tags = models.JSONField(null=True, blank=True)
    subject = models.CharField(max_length=100)

    # READY, PROGRESSING, COMPLETED
    status = models.CharField(max_length=20, default="READY")

    created_at = models.DateTimeField()
    due_date = models.DateTimeField(null=True, blank=True)


class TaskGroup(models.Model):
    id = models.AutoField(primary_key=True)
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=100)
    tags = models.JSONField(null=True, blank=True)

    # READY, PROGRESSING, COMPLETED
    status = models.CharField(max_length=20, default="READY")

    created_at = models.DateTimeField()
    due_date = models.DateTimeField(null=True, blank=True)


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


class GithubStatus(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    status = models.CharField(max_length=20)
    last_update = models.DateTimeField()


class S3ResourceReferenceCheck(models.Model):
    id = models.AutoField(primary_key=True)
    resource_link = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class ProjectInvite(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inviter")
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invitee")

    role = models.CharField(max_length=20)
    created_at = models.DateTimeField()

from django.contrib import admin
from projects.models import Project, ProjectInvite, ProjectMember


# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "status",
        "title",
        "short_description",
        "description",
        "description_resource_links",
        "created_at",
        "due_date",
        "thumbnail_image",
    )
    list_filter = ("status", "owner")
    ordering = ("id", "created_at", "owner", "status")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "owner",
                    "status",
                    "title",
                    "short_description",
                    "description",
                    "description_resource_links",
                    "created_at",
                    "due_date",
                    "thumbnail_image",
                )
            },
        ),
    )


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "user", "role", "created_at")
    list_filter = ("project", "user", "role")
    ordering = ("id", "created_at", "project", "user", "role")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "project",
                    "user",
                    "role",
                    "created_at",
                )
            },
        ),
    )


@admin.register(ProjectInvite)
class ProjectInviteAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "role", "inviter", "invitee", "created_at")
    list_filter = ("inviter", "invitee", "created_at")
    ordering = ("id", "created_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "project",
                    "role",
                    "inviter",
                    "invitee",
                    "created_at",
                )
            },
        ),
    )

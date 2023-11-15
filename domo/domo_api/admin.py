from django.contrib import admin

from .models import (
    GithubStatus,
    Milestone,
    PasswordResetToken,
    Project,
    ProjectMember,
    S3ResourceReferenceCheck,
    SignUpEmailVerifyToken,
    Task,
    TaskGroup,
    User,
    UserKeyword,
    UserStack,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "name",
        "is_active",
        "profile_image_link",
        "short_description",
        "grade",
        "like",
        "rating",
        "github_link",
        "created_at",
        "is_staff",
        "is_superuser",
        "provider",
        "pre_access_token",
    )
    list_filter = ("is_superuser", "created_at")
    search_fields = ("email", "name")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("email", "password", "provider", "pre_access_token")}),
        (
            "Personal Info",
            {
                "fields": (
                    "name",
                    "github_link",
                    "short_description",
                    "description",
                    "description_resource_links",
                    "grade",
                    "like",
                    "rating",
                    "is_active",
                    "profile_image_link",
                    "created_at",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "name"),
            },
        ),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "token", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user",)
    ordering = ("-created_at",)
    fieldsets = ((None, {"fields": ("user", "token", "created_at")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user", "token", "created_at"),
            },
        ),
    )


@admin.register(SignUpEmailVerifyToken)
class EmailVerifyTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "token", "created_at")
    list_filter = ("created_at",)
    search_fields = ("email",)
    ordering = ("-created_at",)
    fieldsets = ((None, {"fields": ("email", "token", "created_at")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "token", "created_at"),
            },
        ),
    )


@admin.register(UserStack)
class UserStackAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "language", "code_amount")
    list_filter = ("user",)
    search_fields = ("language",)
    ordering = ("id",)
    fieldsets = ((None, {"fields": ("user", "language", "code_amount")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user", "language", "code_amount"),
            },
        ),
    )


@admin.register(UserKeyword)
class UserKeywordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "keyword")
    list_filter = ("user",)
    search_fields = ("keyword",)
    ordering = ("id",)
    fieldsets = ((None, {"fields": ("user", "keyword")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user", "keyword"),
            },
        ),
    )


@admin.register(GithubStatus)
class GithubStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "last_update")
    list_filter = ("user",)
    search_fields = ("language",)
    ordering = ("id",)
    fieldsets = ((None, {"fields": ("user", "status", "last_update")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user", "status", "last_update"),
            },
        ),
    )


@admin.register(S3ResourceReferenceCheck)
class S3ResourceReferenceCheckAdmin(admin.ModelAdmin):
    list_display = ("id", "resource_link", "owner")
    list_filter = ("resource_link", "owner")
    ordering = ("id", "owner")
    fieldsets = ((None, {"fields": ("resource_link", "owner")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("resource_link", "owner"),
            },
        ),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "status",
        "title",
        "short_description",
        "description",
        "created_at",
        "like",
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
                    "created_at",
                    "like",
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


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "project",
        "tags",
        "subject",
        "status",
        "created_at",
        "due_date",
    )
    list_filter = ("project", "status")
    ordering = ("id", "created_at", "project", "status")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "project",
                    "tags",
                    "subject",
                    "status",
                    "created_at",
                    "due_date",
                )
            },
        ),
    )


@admin.register(TaskGroup)
class TaskGroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "milestone",
        "title",
        "tags",
        "status",
        "created_at",
        "due_date",
    )
    list_filter = ("milestone", "status")
    ordering = ("id", "created_at", "milestone", "status")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "milestone",
                    "title",
                    "tags",
                    "status",
                    "created_at",
                    "due_date",
                )
            },
        ),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "task_group",
        "title",
        "description",
        "tags",
        "created_at",
        "is_public",
    )
    list_filter = ("owner", "task_group", "is_public")
    ordering = ("id", "created_at", "owner", "task_group", "is_public")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "owner",
                    "task_group",
                    "title",
                    "description",
                    "description_resource_links",
                    "tags",
                    "created_at",
                    "is_public",
                )
            },
        ),
    )

from django.contrib import admin
from tasks.models import Task, TaskGroup


# Register your models here.
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

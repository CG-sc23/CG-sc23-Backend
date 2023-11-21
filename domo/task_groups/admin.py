from django.contrib import admin
from task_groups.models import TaskGroup


@admin.register(TaskGroup)
class TaskGroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "milestone",
        "created_by",
        "title",
        "status",
        "created_at",
    )
    list_filter = ("milestone", "status")
    ordering = ("id", "created_at", "milestone", "status")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "milestone",
                    "created_by",
                    "title",
                    "status",
                    "created_at",
                )
            },
        ),
    )

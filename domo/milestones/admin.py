from django.contrib import admin
from milestones.models import Milestone


# Register your models here.
@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "project",
        "created_by",
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
                    "created_by",
                    "tags",
                    "subject",
                    "status",
                    "created_at",
                    "due_date",
                )
            },
        ),
    )

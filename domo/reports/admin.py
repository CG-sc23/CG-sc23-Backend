from django.contrib import admin
from reports.models import Report


# Register your models here.
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "feed",
        "title",
        "description",
        "created_at",
        "is_active",
    )
    list_filter = ("is_active", "owner")
    ordering = ("id", "created_at", "owner", "is_active")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "owner",
                    "feed",
                    "title",
                    "description",
                    "created_at",
                    "is_active",
                )
            },
        ),
    )

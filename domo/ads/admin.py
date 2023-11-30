from ads.models import Ad
from django.contrib import admin


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "is_active",
        "initial_exposure_count",
        "remaining_exposure_count",
        "requester_email",
        "requester_name",
        "company_email",
        "company_name",
        "purpose",
        "file_link",
        "created_at",
    )
    list_filter = ("is_active", "company_name")
    ordering = ("id", "created_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "is_active",
                    "initial_exposure_count",
                    "remaining_exposure_count",
                    "requester_email",
                    "requester_name",
                    "company_email",
                    "company_name",
                    "purpose",
                    "file_link",
                    "created_at",
                )
            },
        ),
    )

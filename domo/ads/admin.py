from ads.models import Ads
from django.contrib import admin


@admin.register(Ads)
class AdsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "is_active",
        "requester_email",
        "requester_name",
        "company_email",
        "company_name",
        "ads_purpose",
        "ads_file_link",
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
                    "requester_email",
                    "requester_name",
                    "company_email",
                    "company_name",
                    "ads_purpose",
                    "ads_file_link",
                    "created_at",
                )
            },
        ),
    )

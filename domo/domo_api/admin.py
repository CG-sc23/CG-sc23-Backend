from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "name",
        "github_link",
        "short_description",
        "created_at",
        "is_staff",
    )
    list_filter = ("is_superuser", "created_at")
    search_fields = ("email", "name")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "name",
                    "github_link",
                    "short_description",
                    "description",
                    "grade",
                    "like",
                    "rating",
                )
            },
        ),
        ("Permissions", {"fields": ("is_superuser",)}),
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

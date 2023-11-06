from django.contrib import admin

from .models import PasswordResetToken, SignUpEmailVerifyToken, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "name",
        "is_active",
        "has_profile_image",
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
                    "grade",
                    "like",
                    "rating",
                    "is_active",
                    "has_profile_image",
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

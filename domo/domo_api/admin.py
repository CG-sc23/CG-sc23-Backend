from django.contrib import admin

from .models import (
    GithubStatus,
    PasswordResetToken,
    S3ResourceReferenceCheck,
    SignUpEmailVerifyToken,
    User,
    UserStack,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
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

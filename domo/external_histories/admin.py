from django.contrib import admin
from external_histories.models import GithubStatus, UserKeyword, UserStack


# Register your models here.
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
    list_display = ("id", "user", "keyword", "count")
    list_filter = ("user",)
    search_fields = ("keyword",)
    ordering = ("id",)
    fieldsets = ((None, {"fields": ("user", "keyword", "count")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user", "keyword", "count"),
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

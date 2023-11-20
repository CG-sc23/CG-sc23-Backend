from django.contrib import admin
from resources.models import S3ResourceReferenceCheck


# Register your models here.
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

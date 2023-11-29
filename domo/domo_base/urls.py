from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("auths.urls")),
    path("user/", include("users.urls")),
    path("project/", include("projects.urls")),
    path("milestone/", include("milestones.urls")),
    path("external-history/", include("external_histories.urls")),
    path("resource/", include("resources.urls")),
    path("task-group/", include("task_groups.urls")),
    path("task/", include("tasks.urls")),
    path("report/", include("reports.urls")),
]

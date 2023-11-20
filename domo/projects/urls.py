from django.contrib import admin
from django.urls import path
from projects import views as project

urlpatterns = [
    path(
        "v1",
        project.Info.as_view(),
        name="project_info",
    ),
    path(
        "v1/info",
        project.PublicInfo.as_view(),
        name="project_info",
    ),
    path(
        "v1/invite",
        project.Invite.as_view(),
        name="project_invite",
    ),
]

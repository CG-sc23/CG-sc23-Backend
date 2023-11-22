from django.urls import path
from projects import views as project

urlpatterns = [
    path(
        "v1",
        project.Info.as_view(),
        name="project_info",
    ),
    path(
        "v1/<int:project_id>",
        project.Info.as_view(),
        name="project_info_id",
    ),
    path(
        "v1/info/<int:project_id>",
        project.PublicInfo.as_view(),
        name="project_info",
    ),
    path(
        "v1/info/all",
        project.AllInfo.as_view(),
        name="project_all_info",
    ),
    path(
        "v1/invite",
        project.Invite.as_view(),
        name="project_invite",
    ),
    path(
        "v1/<int:project_id>/role",
        project.Role.as_view(),
        name="project_role",
    ),
]

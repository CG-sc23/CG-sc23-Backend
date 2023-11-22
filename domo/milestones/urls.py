from django.urls import path
from milestones import views as milestone

urlpatterns = [
    path(
        "v1/<int:request_id>",
        milestone.Info.as_view(),
        name="milestone_info",
    ),
]

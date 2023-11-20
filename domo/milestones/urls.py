from django.urls import path
from milestones import views as milestone

urlpatterns = [
    path(
        "v1",
        milestone.Info.as_view(),
        name="milestone_info",
    ),
]

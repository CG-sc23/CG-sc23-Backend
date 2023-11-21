from django.urls import path
from task_groups import views as task_group

urlpatterns = [
    path(
        "v1",
        task_group.Info.as_view(),
        name="task_group_info",
    ),
]

from django.urls import path
from tasks import views as task

urlpatterns = [
    path(
        "v1",
        task.Info.as_view(),
        name="task_info",
    ),
]

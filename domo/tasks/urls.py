from django.urls import path
from tasks import views as task

urlpatterns = [
    path(
        "v1/<int:request_id>",
        task.Info.as_view(),
        name="task_info",
    ),
    path(
        "v1/page/<int:page_idx>",
        task.Page.as_view(),
        name="task_info_all",
    ),
]

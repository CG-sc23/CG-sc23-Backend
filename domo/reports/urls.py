from django.urls import path
from reports import views as report

urlpatterns = [
    path(
        "v1/<int:request_id>",
        report.Info.as_view(),
        name="report_info",
    ),
    path(
        "v1/manage",
        report.Manage.as_view(),
        name="report_manage",
    ),
]

import logging
from datetime import datetime, timezone

from common.auth import IsStaff
from common.http_model import SimpleFailResponse, SimpleSuccessResponse
from django.db.transaction import atomic
from django.http import JsonResponse
from pydantic import ValidationError
from reports.http_model import CreateReportRequest, GetAllReportResponse
from reports.models import Report
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from tasks.models import Task

# Create your views here.


@atomic
def create_new_report(request_user, request_task, request_data):
    new_report = Report(
        owner=request_user,
        feed=request_task,
        title=request_data.title,
        description=request_data.description,
        created_at=datetime.now(tz=timezone.utc),
    )
    new_report.save()

    return new_report


class Info(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        task_id = request_id
        try:
            feed = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Can't find task."
                ).model_dump(),
                status=404,
            )

        title = request.data.get("title")
        description = request.data.get("description", None)

        try:
            request_data = CreateReportRequest(
                title=title,
                description=description,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            create_new_report(request.user, feed, request_data)
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating report."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            SimpleSuccessResponse(
                success=True,
            ).model_dump(),
            status=201,
        )


class Manage(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStaff]

    def get(self, request):
        reports = Report.objects.all()

        reports_data = []

        for report in reports:
            owner_data = {
                "id": report.owner.id,
                "email": report.owner.email,
                "name": report.owner.name,
            }

            feed_data = {
                "id": report.feed.id,
                "title": report.feed.title,
            }

            report_data = {
                "id": report.id,
                "owner": owner_data,
                "feed": feed_data,
                "title": report.title,
                "description": report.description,
                "created_at": report.created_at,
                "is_active": report.is_active,
            }

            reports_data.append(report_data)

        return JsonResponse(
            GetAllReportResponse(
                success=True,
                count=len(reports_data),
                reports=reports_data,
            ).model_dump(),
            status=200,
        )

import logging
from datetime import datetime, timezone

from django.db.transaction import atomic
from django.http import JsonResponse
from domo_api.http_model import (
    CreateMilestoneRequest,
    CreateMilestoneResponse,
    ModifyMilestoneRequest,
    SimpleFailResponse,
    SimpleSuccessResponse,
)
from domo_api.models import Milestone, Project, ProjectMember
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView


@atomic
def create_new_milestone(request_user, request_project, request_data):
    new_milestone = Milestone(
        project=request_project,
        created_by=request_user,
        tags=request_data.tags,
        subject=request_data.subject,
        created_at=datetime.now(tz=timezone.utc),
        due_date=request_data.due_date,
    )
    new_milestone.save()

    return new_milestone


class Info(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        project_id = request.GET.get("project-id")
        subject = request.data.get("subject")
        tags = request.data.get("tags", None)
        due_date = request.data.get("due_date", None)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Project not found"
                ).model_dump(),
                status=404,
            )

        try:
            member_role = ProjectMember.objects.get(
                project=project, user=request.user
            ).role
        except:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Permission error"
                ).model_dump(),
                status=401,
            )

        if member_role == "MEMBER":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User must OWNER or MANAGER"
                ).model_dump(),
                status=401,
            )

        try:
            request_data = CreateMilestoneRequest(
                subject=subject,
                tags=tags,
                due_date=due_date,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            new_milestone = create_new_milestone(request.user, project, request_data)
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating milestone."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            CreateMilestoneResponse(
                success=True,
                milestone_id=new_milestone.id,
                status=new_milestone.status,
                subject=new_milestone.subject,
                tags=new_milestone.tags,
                created_at=new_milestone.created_at,
                due_date=new_milestone.due_date,
            ).model_dump(),
            status=201,
        )

    def put(self, request):
        project_id = request.GET.get("project-id")
        milestone_id = request.GET.get("milestone-id")

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Project not found"
                ).model_dump(),
                status=404,
            )

        try:
            milestone = Milestone.objects.get(id=milestone_id)
        except Milestone.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Milestone not found"
                ).model_dump(),
                status=404,
            )

        try:
            member_role = ProjectMember.objects.get(
                project=project, user=request.user
            ).role
        except:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Permission error"
                ).model_dump(),
                status=401,
            )

        if member_role == "MEMBER":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User must OWNER or MANAGER"
                ).model_dump(),
                status=401,
            )

        subject = request.data.get("subject")
        status = request.data.get("status")
        if not status:
            status = milestone.status
        tags = request.data.get("tags", None)
        due_date = request.data.get("due_date", None)

        try:
            request_data = ModifyMilestoneRequest(
                subject=subject,
                status=status,
                tags=tags,
                due_date=due_date,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            milestone.subject = request_data.subject or milestone.subject
            milestone.status = request_data.status or milestone.status
            milestone.tags = request_data.tags or milestone.tags
            milestone.due_date = request_data.due_date or milestone.due_date

            milestone.save()
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error modifying milestone."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            CreateMilestoneResponse(
                success=True,
                milestone_id=milestone.id,
                status=milestone.status,
                subject=milestone.subject,
                tags=milestone.tags,
                created_at=milestone.created_at,
                due_date=milestone.due_date,
            ).model_dump(),
            status=201,
        )
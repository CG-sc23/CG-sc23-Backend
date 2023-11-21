import logging
from datetime import datetime, timezone

from common.http_model import SimpleFailResponse
from django.db.transaction import atomic
from django.http import JsonResponse
from milestones.models import Milestone
from projects.models import Project, ProjectMember
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from task_groups.http_model import (
    CreateTaskGroupRequest,
    CreateTaskGroupResponse,
    GetTaskGroupResponse,
    ModifyTaskGroupRequest,
)
from task_groups.models import TaskGroup


@atomic
def create_new_task_group(request_user, request_milestone, request_data):
    new_task_group = TaskGroup(
        milestone=request_milestone,
        created_by=request_user,
        title=request_data.title,
        created_at=datetime.now(tz=timezone.utc),
    )
    new_task_group.save()

    return new_task_group


class Info(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        milestone_id = request.GET.get("milestone-id")
        title = request.data.get("title")

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
            project = Project.objects.get(milestone=milestone)
            member_role = ProjectMember.objects.get(
                project=project, user=request.user
            ).role
        except:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Permission error"
                ).model_dump(),
                status=403,
            )

        if member_role == "MEMBER":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User must OWNER or MANAGER"
                ).model_dump(),
                status=403,
            )

        try:
            request_data = CreateTaskGroupRequest(
                title=title,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            new_task_group = create_new_task_group(
                request.user, milestone, request_data
            )
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating task group."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            CreateTaskGroupResponse(
                success=True,
                task_group_id=new_task_group.id,
                status=new_task_group.status,
                title=new_task_group.title,
                created_at=new_task_group.created_at,
            ).model_dump(),
            status=201,
        )

    def put(self, request):
        task_group_id = request.GET.get("task-group-id")

        try:
            task_group = TaskGroup.objects.get(id=task_group_id)
        except TaskGroup.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Task group not found"
                ).model_dump(),
                status=404,
            )

        milestone = task_group.milestone
        project = milestone.project

        try:
            member_role = ProjectMember.objects.get(
                project=project, user=request.user
            ).role
        except:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Permission error"
                ).model_dump(),
                status=403,
            )

        if member_role == "MEMBER":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User must OWNER or MANAGER"
                ).model_dump(),
                status=403,
            )

        title = request.data.get("title")
        status = request.data.get("status")
        if not status:
            status = milestone.status

        try:
            request_data = ModifyTaskGroupRequest(
                title=title,
                status=status,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            task_group.title = request_data.title or task_group.title
            task_group.status = request_data.status or task_group.status
            task_group.save()
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error modifying task group."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            CreateTaskGroupResponse(
                success=True,
                task_group_id=task_group.id,
                status=task_group.status,
                title=task_group.title,
                created_at=task_group.created_at,
            ).model_dump(),
            status=201,
        )

    def get(self, request):
        task_group_id = request.GET.get("task-group-id")

        try:
            task_group = TaskGroup.objects.get(id=task_group_id)
        except TaskGroup.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Task group not found"
                ).model_dump(),
                status=404,
            )

        milestone = task_group.milestone
        project = milestone.project

        try:
            member_role = ProjectMember.objects.get(
                project=project, user=request.user
            ).role
        except:
            member_role = "NOTHING"

        created_data = {
            "id": task_group.created_by.id,
            "name": task_group.created_by.name,
        }

        project_data = {"id": project.id, "title": project.title}
        milestone_data = {"id": milestone.id, "subject": milestone.subject}

        return JsonResponse(
            GetTaskGroupResponse(
                success=True,
                task_group_id=task_group.id,
                project=project_data,
                milestone=milestone_data,
                created_by=created_data,
                status=task_group.status,
                title=task_group.title,
                created_at=task_group.created_at,
                permission=member_role,
            ).model_dump(),
            status=200,
        )
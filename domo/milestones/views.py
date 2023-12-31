import json
import logging
from datetime import datetime, timezone

from common.http_model import SimpleFailResponse, SimpleSuccessResponse
from django.db.transaction import atomic
from django.http import JsonResponse
from milestones.http_model import (
    CreateMilestoneRequest,
    CreateMilestoneResponse,
    GetMilestoneResponse,
    ModifyMilestoneRequest,
)
from milestones.models import Milestone
from projects.models import Project, ProjectMember
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from task_groups.models import TaskGroup
from tasks.models import Task


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

    def post(self, request, request_id):
        project_id = request_id
        subject = request.data.get("subject")
        tags = request.data.get("tags", None)
        if tags:
            tags = json.loads(tags)
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

        request_data.due_date = request_data.due_date.replace(
            hour=14, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
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
                id=new_milestone.id,
                status=new_milestone.status,
                subject=new_milestone.subject,
                tags=new_milestone.tags,
                created_at=new_milestone.created_at,
                due_date=new_milestone.due_date,
            ).model_dump(),
            status=201,
        )

    def put(self, request, request_id):
        milestone_id = request_id

        try:
            milestone = Milestone.objects.get(id=milestone_id)
        except Milestone.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Milestone not found"
                ).model_dump(),
                status=404,
            )

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

        subject = request.data.get("subject")
        status = request.data.get("status")
        if not status:
            status = milestone.status
        tags = request.data.get("tags", None)
        if tags:
            tags = json.loads(tags)
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

        if request_data.due_date:
            request_data.due_date = request_data.due_date.replace(
                hour=14, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
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
                id=milestone.id,
                status=milestone.status,
                subject=milestone.subject,
                tags=milestone.tags,
                created_at=milestone.created_at,
                due_date=milestone.due_date,
            ).model_dump(),
            status=201,
        )

    def get(self, request, request_id):
        milestone_id = request_id

        try:
            milestone = Milestone.objects.get(id=milestone_id)
        except Milestone.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Milestone not found"
                ).model_dump(),
                status=404,
            )

        project = milestone.project

        try:
            member_role = ProjectMember.objects.get(
                project=project, user=request.user
            ).role
        except:
            member_role = "NOTHING"

        created_data = {
            "id": milestone.created_by.id,
            "name": milestone.created_by.name,
        }

        project_data = {
            "id": project.id,
            "title": project.title,
            "thumbnail_image": project.thumbnail_image,
        }

        task_groups = TaskGroup.objects.filter(milestone=milestone)

        task_group_datas = []

        for task_group in task_groups:
            tasks = Task.objects.filter(task_group=task_group)

            task_datas = []

            for task in tasks:
                task_data = {
                    "id": task.id,
                    "title": task.title,
                }

                task_datas.append(task_data)

            task_group_data = {
                "id": task_group.id,
                "title": task_group.title,
                "status": task_group.status,
                "created_at": task_group.created_at,
                "due_date": task_group.due_date,
                "tasks": task_datas,
            }

            task_group_datas.append(task_group_data)

        return JsonResponse(
            GetMilestoneResponse(
                success=True,
                id=milestone.id,
                project=project_data,
                created_by=created_data,
                status=milestone.status,
                subject=milestone.subject,
                tags=milestone.tags,
                created_at=milestone.created_at,
                due_date=milestone.due_date,
                task_groups=task_group_datas,
                permission=member_role,
            ).model_dump(),
            status=200,
        )

    def delete(self, request, request_id):
        milestone_id = request_id

        try:
            milestone = Milestone.objects.get(id=milestone_id)
        except Milestone.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Milestone not found"
                ).model_dump(),
                status=404,
            )

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

        try:
            task_groups = TaskGroup.objects.filter(milestone=milestone)
            for task_group in task_groups:
                tasks_cnt = Task.objects.filter(task_group=task_group).count()
                if tasks_cnt > 0:
                    return JsonResponse(
                        SimpleFailResponse(
                            success=False,
                            reason="This milestone has tasks. Please delete all tasks.",
                        ).model_dump(),
                        status=400,
                    )
            milestone.delete()
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error deleting milestone."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            SimpleSuccessResponse(
                success=True,
            ).model_dump(),
            status=200,
        )

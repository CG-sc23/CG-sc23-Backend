import json
import logging
from datetime import datetime, timezone

from common.http_model import SimpleFailResponse
from common.s3.handler import GeneralHandler
from django.db.transaction import atomic
from django.http import JsonResponse
from projects.models import ProjectMember
from pydantic import ValidationError
from resources.models import S3ResourceReferenceCheck
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from task_groups.models import TaskGroup
from tasks.http_model import (
    CreateTaskRequest,
    CreateTaskResponse,
    GetTaskAllResponse,
    GetTaskResponse,
    ModifyTaskRequest,
)
from tasks.models import Task


@atomic
def create_new_task(request_user, request_task_group, request_data):
    new_task = Task(
        owner=request_user,
        task_group=request_task_group,
        title=request_data.title,
        description=request_data.description,
        description_resource_links=request_data.description_resource_links,
        created_at=datetime.now(tz=timezone.utc),
        tags=request_data.tags,
        is_public=request_data.is_public,
    )
    new_task.save()

    return new_task


class Info(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        task_group_id = request.GET.get("task-group-id")
        title = request.data.get("title")
        description = request.data.get("description", None)
        description_resource_links = request.data.get(
            "description_resource_links", None
        )
        if description_resource_links:
            description_resource_links = json.loads(description_resource_links)

        tags = request.data.get("tags", None)
        if tags:
            tags = json.loads(tags)

        is_public = request.data.get("is_public", True)

        try:
            task_group = TaskGroup.objects.get(id=task_group_id)
        except TaskGroup.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Task group not found."
                ).model_dump(),
                status=404,
            )

        milestone = task_group.milestone
        project = milestone.project

        try:
            ProjectMember.objects.get(project=project, user=request.user)
        except:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Permission error"
                ).model_dump(),
                status=403,
            )

        try:
            request_data = CreateTaskRequest(
                task_group=task_group,
                title=title,
                description=description,
                description_resource_links=description_resource_links,
                tags=tags,
                is_public=is_public,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        if isinstance(request_data.description_resource_links, list):
            s3_handler = GeneralHandler("resource")
            if not s3_handler.check_resource_links(
                request_data.description_resource_links
            ):
                return JsonResponse(
                    SimpleFailResponse(
                        success=False,
                        reason="Invalid request.",
                    ).model_dump(),
                    status=400,
                )
            for resource_link in request_data.description_resource_links:
                try:
                    S3ResourceReferenceCheck.objects.get(resource_link=resource_link)
                except S3ResourceReferenceCheck.DoesNotExist:
                    S3ResourceReferenceCheck.objects.create(
                        resource_link=resource_link,
                        owner=request.user,
                    )

        try:
            new_task = create_new_task(request.user, task_group, request_data)
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating task."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            CreateTaskResponse(
                success=True,
                id=new_task.id,
                title=new_task.title,
                description=new_task.description,
                description_resource_links=new_task.description_resource_links,
                created_at=new_task.created_at,
                tags=new_task.tags,
                is_public=new_task.is_public,
            ).model_dump(),
            status=201,
        )

    def put(self, request):
        task_id = request.GET.get("task-id")
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Can't find Task."
                ).model_dump(),
                status=404,
            )

        try:
            user = request.user
            if user != task.owner:
                raise PermissionError
        except:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Permission error"
                ).model_dump(),
                status=403,
            )
        title = request.data.get("title", None)
        description = request.data.get("description", None)
        description_resource_links = request.data.get(
            "description_resource_links", None
        )
        if description_resource_links:
            description_resource_links = json.loads(description_resource_links)

        tags = request.data.get("tags", None)
        if tags:
            tags = json.loads(tags)
        is_public = request.data.get("is_public", None)

        try:
            request_data = ModifyTaskRequest(
                title=title,
                description=description,
                description_resource_links=description_resource_links,
                tags=tags,
                is_public=is_public,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        # description에 media가 있을경우, validation check가 필요하다.
        # 이후 owner를 지정한다.
        if isinstance(request_data.description_resource_links, list):
            s3_handler = GeneralHandler("resource")
            if not s3_handler.check_resource_links(
                request_data.description_resource_links
            ):
                return JsonResponse(
                    SimpleFailResponse(
                        success=False,
                        reason="Invalid request.",
                    ).model_dump(),
                    status=400,
                )
            for resource_link in request_data.description_resource_links:
                try:
                    S3ResourceReferenceCheck.objects.get(resource_link=resource_link)
                except S3ResourceReferenceCheck.DoesNotExist:
                    S3ResourceReferenceCheck.objects.create(
                        resource_link=resource_link,
                        owner=request.user,
                    )

            task_description_resource_links = task.description_resource_links
            if task_description_resource_links:
                for resource_link in task_description_resource_links:
                    ref_check_obj = S3ResourceReferenceCheck.objects.get(
                        resource_link=resource_link
                    )
                    if (
                        ref_check_obj.resource_link
                        not in request_data.description_resource_links
                        and ref_check_obj.owner == request.user
                    ):
                        ref_check_obj.delete()
                        s3_handler.remove_resource(resource_link)

        try:
            task.title = request_data.title or task.title
            task.description = request_data.description or task.description
            task.description_resource_links = (
                request_data.description_resource_links
                or task.description_resource_links
            )
            task.tags = request_data.tags or task.tags
            task.is_public = request_data.is_public or task.is_public
            task.save()

        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error modifying task."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            CreateTaskResponse(
                success=True,
                task_id=task.id,
                title=task.title,
                description=task.description,
                description_resource_links=task.description_resource_links,
                created_at=task.created_at,
                tags=task.tags,
                is_public=task.is_public,
            ).model_dump(),
            status=201,
        )

    def get(self, request):
        task_id = request.GET.get("task-id")
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Can't find Task."
                ).model_dump(),
                status=404,
            )

        task_group = task.task_group
        milestone = task_group.milestone
        project = milestone.project

        try:
            member_role = ProjectMember.objects.get(
                project=project, user=request.user
            ).role
        except:
            if not task.is_public:
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="Permission error"
                    ).model_dump(),
                    status=403,
                )

            member_role = "NOTHING"

        created_data = {
            "id": task.owner.id,
            "name": task.owner.name,
        }

        project_data = {
            "id": project.id,
            "title": project.title,
            "thumbnail_image": project.thumbnail_image,
        }

        milestone_data = {"id": milestone.id, "subject": milestone.subject}

        task_group_data = {"id": task_group.id, "title": task_group.title}

        project_members = ProjectMember.objects.filter(project=project)

        project_member_datas = []

        for member in project_members:
            project_member_data = {
                "id": member.user.id,
                "email": member.user.email,
                "name": member.user.name,
                "profile_image_link": member.user.profile_image_link,
                "profile_image_updated_at": member.user.profile_image_updated_at,
            }

            project_member_datas.append(project_member_data)

        return JsonResponse(
            GetTaskResponse(
                success=True,
                id=task.id,
                project=project_data,
                milestone=milestone_data,
                task_group=task_group_data,
                owner=created_data,
                title=task.title,
                description=task.description,
                description_resource_links=task.description_resource_links,
                created_at=task.created_at,
                tags=task.tags,
                members=project_member_datas,
                is_public=task.is_public,
                permission=member_role,
            ).model_dump(),
            status=200,
        )


class Page(APIView):
    def get(self, request, page_idx):
        all_task = Task.objects.filter(is_public=True).order_by("-created_at")
        tasks_response = []

        for i in range((page_idx - 1) * 6, page_idx * 6):
            if i >= len(all_task):
                break
            task = all_task[i]
            task_group = task.task_group
            milestone = task_group.milestone
            project = milestone.project

            created_data = {
                "id": task.owner.id,
                "name": task.owner.name,
                "profile_image_link": task.owner.profile_image_link,
                "profile_image_updated_at": task.owner.profile_image_updated_at,
            }

            project_data = {"id": project.id, "title": project.title}
            milestone_data = {"id": milestone.id, "subject": milestone.subject}
            task_group_data = {"id": task_group.id, "title": task_group.title}

            tasks_response.append(
                {
                    "id": task.id,
                    "project": project_data,
                    "milestone": milestone_data,
                    "task_group": task_group_data,
                    "owner": created_data,
                    "title": task.title,
                    "description": task.description,
                    "description_resource_links": task.description_resource_links,
                    "created_at": task.created_at,
                    "tags": task.tags,
                }
            )
        return JsonResponse(
            GetTaskAllResponse(
                success=True, total_count=len(all_task), tasks=tasks_response
            ).model_dump(),
            status=200,
        )

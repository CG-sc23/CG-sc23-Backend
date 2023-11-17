import logging
from datetime import datetime, timezone

from django.db.transaction import atomic
from django.http import JsonResponse
from domo_api.http_model import (
    CreateProjectRequest,
    CreateProjectResponse,
    GetProjectResponse,
    MakeProjectInviteRequest,
    ModifyProjectRequest,
    SimpleFailResponse,
    SimpleSuccessResponse,
)
from domo_api.models import (
    Project,
    ProjectInvite,
    ProjectMember,
    S3ResourceReferenceCheck,
)
from domo_api.s3.handler import GeneralHandler
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


@atomic
def create_new_project(request_user, request_data):
    new_project = Project(
        owner=request_user,
        title=request_data.title,
        short_description=request_data.short_description,
        description=request_data.description,
        description_resource_links=request_data.description_resource_links,
        created_at=datetime.now(tz=timezone.utc),
        due_date=request_data.due_date,
        thumbnail_image=request_data.thumbnail_image,
    )
    new_project.save()

    ProjectMember(
        project=new_project,
        user=request_user,
        role="OWNER",
        created_at=datetime.now(tz=timezone.utc),
    ).save()

    return new_project


class Info(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        short_description = request.data.get("short_description", None)
        description = request.data.get("description", None)
        description_resource_links = request.data.get(
            "description_resource_links", None
        )
        due_date = request.data.get("due_date", None)
        thumbnail_image = request.data.get("thumbnail_image", None)

        try:
            request_data = CreateProjectRequest(
                title=title,
                short_description=short_description,
                description=description,
                description_resource_links=description_resource_links,
                due_date=due_date,
                thumbnail_image=thumbnail_image,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        if thumbnail_image:
            s3_handler = GeneralHandler()
            if not s3_handler.check_resource_links(request_data.thumbnail_image):
                return JsonResponse(
                    SimpleFailResponse(
                        success=False,
                        reason="Invalid thumbnail image.",
                    ).model_dump(),
                    status=400,
                )

        try:
            new_project = create_new_project(request.user, request_data)
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating project."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            CreateProjectResponse(
                success=True,
                project_id=new_project.id,
                status=new_project.status,
                title=new_project.title,
                short_description=new_project.short_description,
                description=new_project.description,
                description_resource_links=new_project.description_resource_links,
                created_at=new_project.created_at,
                due_date=new_project.due_date,
                thumbnail_image=new_project.thumbnail_image,
            ).model_dump(),
            status=201,
        )

    def put(self, request):
        project_id = request.GET.get("project-id")
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Can't find project."
                ).model_dump(),
                status=404,
            )

        if request.user != project.owner:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Permission error"
                ).model_dump(),
                status=401,
            )

        title = request.data.get("title")
        status = request.data.get("status", None)
        if not status:
            status = project.status
        short_description = request.data.get("short_description", None)
        description = request.data.get("description", None)
        description_resource_links = request.data.get(
            "description_resource_links", None
        )
        due_date = request.data.get("due_date", None)
        thumbnail_image = request.data.get("thumbnail_image", None)

        try:
            request_data = ModifyProjectRequest(
                title=title,
                status=status,
                short_description=short_description,
                description=description,
                description_resource_links=description_resource_links,
                due_date=due_date,
                thumbnail_image=thumbnail_image,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        if thumbnail_image:
            s3_handler = GeneralHandler()
            if not s3_handler.check_resource_links(request_data.thumbnail_image):
                return JsonResponse(
                    SimpleFailResponse(
                        success=False,
                        reason="Invalid thumbnail image.",
                    ).model_dump(),
                    status=400,
                )

        # description에 media가 있을경우, validation check가 필요하다.
        # 이후 owner를 지정한다.
        if isinstance(request_data.description_resource_links, list):
            s3_handler = GeneralHandler()
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

            user_description_resource_links = request.user.description_resource_links
            if user_description_resource_links:
                for resource_link in user_description_resource_links:
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
            project.title = request_data.title or project.title
            project.status = request_data.status or project.status
            project.short_description = (
                request_data.short_description or project.short_description
            )
            project.description = request_data.description or project.description
            project.description_resource_links = (
                request_data.description_resource_links
                or project.description_resource_links
            )
            project.thumbnail_image = (
                request_data.thumbnail_image or project.thumbnail_image
            )
            project.due_date = request_data.due_date or project.due_date
            project.save()

        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating project."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            CreateProjectResponse(
                success=True,
                project_id=project.id,
                status=project.status,
                title=project.title,
                short_description=project.short_description,
                description=project.description,
                description_resource_links=project.description_resource_links,
                created_at=project.created_at,
                due_date=project.due_date,
                thumbnail_image=project.thumbnail_image,
            ).model_dump(),
            status=200,
        )


class PublicInfo(APIView):
    def get(self, request):
        project_id = request.GET.get("project-id")
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Can't find project."
                ).model_dump(),
                status=404,
            )

        owner_data = {
            "id": project.owner.id,
            "name": project.owner.name,
        }

        return JsonResponse(
            GetProjectResponse(
                success=True,
                owner=owner_data,
                project_id=project.id,
                status=project.status,
                title=project.title,
                short_description=project.short_description,
                description=project.description,
                description_resource_links=project.description_resource_links,
                created_at=project.created_at,
                due_date=project.due_date,
                thumbnail_image=project.thumbnail_image,
            ).model_dump(),
            status=200,
        )


class Invite(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get("project_id")
        invitee_id = request.data.get("invitee_id")
        role = request.data.get("role")

        try:
            request_data = MakeProjectInviteRequest(
                project_id=project_id,
                invitee_id=invitee_id,
                role=role,
            )
            if request_data.role not in ["MANAGER", "MEMBER"]:
                raise ValidationError
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        if not Project.objects.filter(
            id=request_data.project_id,
        ).exists():
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Project does not exist."
                ).model_dump(),
                status=404,
            )
        if ProjectMember.objects.filter(
            project_id=project_id, user_id=invitee_id
        ).exists():
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User already in project."
                ).model_dump(),
                status=400,
            )
        if not ProjectMember.objects.filter(
            project_id=project_id, user_id=request.user.id
        ).exists():
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="You are not in requested project."
                ).model_dump(),
                status=403,
            )
        if (
            request_data.role == "MANAGER"
            and not ProjectMember.objects.filter(
                project_id=project_id,
                user_id=request.user.id,
                role__in=["OWNER", "MANAGER"],
            ).exists()
        ):
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="You are not manager of requested project."
                ).model_dump(),
                status=403,
            )
        try:
            ProjectInvite(
                project_id=project_id,
                inviter_id=request.user.id,
                invitee_id=invitee_id,
                role=request_data.role,
                created_at=datetime.now(tz=timezone.utc),
            ).save()
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error inviting user."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            SimpleSuccessResponse(
                success=True,
            ).model_dump(),
            status=200,
        )

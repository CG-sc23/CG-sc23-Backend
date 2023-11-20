import json
from datetime import datetime, timezone

from common.http_model import SimpleFailResponse, SimpleSuccessResponse
from common.s3.handler import GeneralHandler, upload_profile_image
from common.tasks import update_github_history
from django.db.transaction import atomic
from django.http import JsonResponse
from projects.http_model import GetAllProjectResponse, ReplyProjectInviteRequest
from projects.models import Project, ProjectInvite, ProjectMember, User
from pydantic import ValidationError
from resources.models import S3ResourceReferenceCheck
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.http_model import (
    GetUserDetailInfoResponse,
    GetUserInfoResponse,
    GetUserPublicDetailInfoResponse,
    ModifyUserDetailInfoRequest,
)


class Info(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = GetUserInfoResponse(
            success=True,
            user_id=request.user.id,
            email=request.user.email,
            name=request.user.name,
            profile_image_link=request.user.profile_image_link,
        )
        return JsonResponse(response.model_dump(), status=200)

    def delete(self, request):
        request.user.is_active = False
        request.user.save()

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
        )


class DetailInfo(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = GetUserDetailInfoResponse(
            success=True,
            github_link=request.user.github_link,
            short_description=request.user.short_description,
            description=request.user.description,
            description_resource_links=request.user.description_resource_links,
            grade=request.user.grade,
            like=request.user.like,
            rating=request.user.rating,
            provider=request.user.provider,
        )
        return JsonResponse(response.model_dump(), status=200)

    @atomic
    def put(self, request):
        name = request.data.get("name", None)
        github_link = request.data.get("github_link", None)
        short_description = request.data.get("short_description", None)
        description = request.data.get("description", None)
        description_resource_links = request.data.get(
            "description_resource_links", None
        )
        if description_resource_links:
            description_resource_links = json.loads(description_resource_links)

        data_dict = {
            "name": name,
            "github_link": github_link,
            "short_description": short_description,
            "description": description,
            "description_resource_links": description_resource_links,
        }

        try:
            request_data = ModifyUserDetailInfoRequest(**data_dict)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        # If profile image exists, upload to S3 first
        profile_image_link = None
        if "profile_image" in request.FILES:
            profile_image_link = upload_profile_image(
                request_data, request.FILES["profile_image"]
            )
            # This is a JsonResponse for Exception
            if isinstance(profile_image_link, JsonResponse):
                return profile_image_link

        if profile_image_link:
            request.user.profile_image_link = profile_image_link

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

        if request_data.github_link:
            update_github_history.delay(request.user.id, request_data.github_link)

        request.user.name = request_data.name or request.user.name
        request.user.github_link = request_data.github_link or request.user.github_link
        request.user.short_description = (
            request_data.short_description or request.user.short_description
        )
        request.user.description = request_data.description or request.user.description
        if request_data.description_resource_links:
            request.user.description_resource_links = (
                request_data.description_resource_links
            )
        elif isinstance(request_data.description_resource_links, list):
            request.user.description_resource_links = None

        request.user.save()

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=200,
        )


class PublicDetailInfo(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User does not exist."
                ).model_dump(),
                status=404,
            )

        response = GetUserPublicDetailInfoResponse(
            success=True,
            email=user.email,
            name=user.name,
            github_link=user.github_link,
            short_description=user.short_description,
            description=user.description,
            description_resource_links=user.description_resource_links,
            grade=user.grade,
            like=user.like,
            rating=user.rating,
            provider=user.provider,
        )
        return JsonResponse(
            response.model_dump(),
            status=200,
        )


class ProjectInfo(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_list = Project.objects.filter(
            projectmember__user=request.user,
        ).order_by("created_at")

        projects = []
        for project in project_list:
            projects.append(project.detail())

        response = GetAllProjectResponse(
            success=True, count=len(projects), projects=projects
        )
        return JsonResponse(response.model_dump(), status=200)


class Inviter(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invited_project_list = ProjectInvite.objects.filter(
            inviter=request.user,
        ).order_by("-created_at")

        response_list = []
        for invite_project in invited_project_list:
            response_list.append(
                {
                    "project_id": invite_project.project.id,
                    "invitee_id": invite_project.invitee.id,
                    "role": invite_project.role,
                    "created_at": invite_project.created_at,
                }
            )

        return JsonResponse(response_list, status=200, safe=False)


class Invitee(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get("project_id")
        inviter_id = request.data.get("inviter_id")
        accept = request.data.get("accept")

        data_dict = {
            "project_id": project_id,
            "inviter_id": inviter_id,
            "accept": accept,
        }

        try:
            request_data = ReplyProjectInviteRequest(**data_dict)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        if not ProjectInvite.objects.filter(
            project_id=request_data.project_id,
            inviter_id=request_data.inviter_id,
            invitee=request.user,
        ).exists():
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invite does not exist."
                ).model_dump(),
                status=404,
            )

        if request_data.accept:
            ProjectMember.objects.create(
                project_id=request_data.project_id,
                user=request.user,
                role=ProjectInvite.objects.get(
                    project_id=request_data.project_id,
                    inviter_id=request_data.inviter_id,
                    invitee=request.user,
                ).role,
                created_at=datetime.now(tz=timezone.utc),
            )
            ProjectInvite.objects.get(
                project_id=request_data.project_id,
                inviter_id=request_data.inviter_id,
                invitee=request.user,
            ).delete()
        else:
            ProjectInvite.objects.get(
                project_id=request_data.project_id,
                inviter_id=request_data.inviter_id,
                invitee=request.user,
            ).delete()

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=200,
        )

    def get(self, request):
        invited_project_list = ProjectInvite.objects.filter(
            invitee=request.user,
        ).order_by("-created_at")

        response_list = []
        for invite_project in invited_project_list:
            response_list.append(
                {
                    "project_id": invite_project.project.id,
                    "inviter_id": invite_project.inviter.id,
                    "role": invite_project.role,
                    "created_at": invite_project.created_at,
                }
            )

        return JsonResponse(response_list, status=200, safe=False)

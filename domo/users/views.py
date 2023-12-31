import json
import random
from datetime import datetime, timezone

from common.const import ReturnCode
from common.http_model import SimpleFailResponse, SimpleSuccessResponse
from common.s3.handler import GeneralHandler
from common.tasks import update_github_history
from django.db.models import Q
from django.db.transaction import atomic
from django.http import JsonResponse
from external_histories.models import GithubStatus
from projects.http_model import GetAllProjectResponse
from projects.models import Project, ProjectInvite, ProjectMember, User
from pydantic import ValidationError
from resources.models import S3ResourceReferenceCheck
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.http_model import (
    GetProjectInviteResponse,
    GetSearchResponse,
    GetUserDetailInfoResponse,
    GetUserInfoResponse,
    GetUserPublicDetailInfoResponse,
    GetUserRecommendResponse,
    GetUserTaskInfoResponse,
    ModifyUserDetailInfoRequest,
    ReplyProjectInviteRequest,
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
            profile_image_updated_at=request.user.profile_image_updated_at,
            provider=request.user.provider,
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
        profile_image_link = request.data.get("profile_image_link", None)

        if description_resource_links:
            description_resource_links = json.loads(description_resource_links)

        data_dict = {
            "name": name,
            "github_link": github_link,
            "short_description": short_description,
            "description": description,
            "description_resource_links": description_resource_links,
            "profile_image_link": profile_image_link,
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

        # 위와 마찬가지로 profile image가 있을경우, validation check가 필요하다.
        profile_image_modifier = GeneralHandler("profile")

        if request_data.profile_image_link is None:
            pass
        elif request_data.profile_image_link == "" and request.user.profile_image_link:
            profile_image_modifier.remove_resource(request.user.profile_image_link)
        else:
            if not profile_image_modifier.check_resource_links(
                request_data.profile_image_link
            ):
                return JsonResponse(
                    SimpleFailResponse(
                        success=False,
                        reason="Invalid request.",
                    ).model_dump(),
                    status=400,
                )
            if (
                request.user.profile_image_link
                and request_data.profile_image_link != request.user.profile_image_link
            ):
                profile_image_modifier.remove_resource(request.user.profile_image_link)

        if (
            request_data.github_link
            and request_data.github_link != request.user.github_link
        ):
            if not GithubStatus.objects.filter(user_id=request.user.id).exists():
                GithubStatus.objects.create(
                    user_id=request.user.id,
                    status=ReturnCode.GITHUB_STATUS_IN_PROGRESS,
                    last_update=datetime.now(tz=timezone.utc),
                )
            update_github_history.delay(request.user.id, request_data.github_link)

        request.user.name = request_data.name or request.user.name
        request.user.github_link = request_data.github_link
        request.user.short_description = (
            request_data.short_description or request.user.short_description
        )
        request.user.description = request_data.description or request.user.description

        if request_data.profile_image_link == "":
            request.user.profile_image_link = None
            request.user.profile_image_updated_at = None
        else:
            request.user.profile_image_link = (
                request_data.profile_image_link or request.user.profile_image_link
            )
            request.user.profile_image_updated_at = datetime.now(tz=timezone.utc)

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


class TaskInfo(APIView):
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
        try:
            if request.user == user:
                count = user.task_set.count()
                tasks = [task.detail() for task in user.task_set.all()]
            else:
                raise TypeError
        except TypeError:
            count = user.task_set.filter(is_public=True).count()
            tasks = [task.detail() for task in user.task_set.filter(is_public=True)]

        response = GetUserTaskInfoResponse(
            success=True,
            count=count,
            tasks=tasks,
        )
        return JsonResponse(
            response.model_dump(),
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
            profile_image_link=user.profile_image_link,
            profile_image_updated_at=user.profile_image_updated_at,
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

        project_list = Project.objects.filter(
            projectmember__user=user,
        ).order_by("created_at")

        projects = []
        for project in project_list:
            project_dict = {"project": project.detail()}

            project_members = ProjectMember.objects.filter(project=project)
            project_member_datas = []

            for member in project_members:
                project_member_data = {
                    "id": member.user.id,
                    "name": member.user.name,
                    "email": member.user.email,
                    "profile_image_link": member.user.profile_image_link,
                    "profile_image_updated_at": member.user.profile_image_updated_at,
                }
                project_member_datas.append(project_member_data)
            project_dict["project"]["members"] = project_member_datas
            projects.append(project_dict)

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
                    "invitee_email": invite_project.invitee.email,
                    "created_at": invite_project.created_at,
                }
            )

        response = GetProjectInviteResponse(success=True, result=response_list)
        return JsonResponse(response.model_dump(), status=200)


class Invitee(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get("project_id")
        inviter_email = request.data.get("inviter_email")
        accept = request.data.get("accept")

        data_dict = {
            "project_id": project_id,
            "inviter_email": inviter_email,
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
            inviter__email=request_data.inviter_email,
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
                role="MEMBER",
                created_at=datetime.now(tz=timezone.utc),
            )
            ProjectInvite.objects.filter(
                project_id=request_data.project_id,
                invitee=request.user,
            ).delete()
        else:
            ProjectInvite.objects.filter(
                project_id=request_data.project_id,
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
                    "inviter_email": invite_project.inviter.email,
                    "created_at": invite_project.created_at,
                }
            )
        response = GetProjectInviteResponse(success=True, result=response_list)
        return JsonResponse(response.model_dump(), status=200)


class Search(APIView):
    def get(self, request):
        request_data = request.GET.get("request-data")
        users = (
            User.objects.filter(
                Q(email__istartswith=request_data) | Q(name__istartswith=request_data)
            )
            .exclude(is_staff=True)
            .distinct()
        )

        result = []
        for user in users:
            result.append(
                {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "profile_image_link": user.profile_image_link,
                    "profile_image_updated_at": user.profile_image_updated_at,
                }
            )

        result = GetSearchResponse(success=True, result=result)
        return JsonResponse(
            result.model_dump(),
            status=200,
        )


class Recommend(APIView):
    def recommend_user(self, users):
        all_user = []

        for user in users:
            all_user.append(user)

        count = 6

        if len(all_user) < 6:
            count = len(all_user)

        recommended_user = random.sample(all_user, count)

        return recommended_user

    def get(self, request):
        try:
            users = User.objects.filter(is_staff=False).exclude(id=request.user.id)
        except User.DoesNotExist:
            users = User.objects.filter(is_staff=False)

        recommended_users = self.recommend_user(users)

        user_datas = []

        for user in recommended_users:
            user_data = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "profile_image_link": user.profile_image_link,
                "profile_image_updated_at": user.profile_image_updated_at,
                "short_description": user.short_description,
            }

            user_datas.append(user_data)

        result = GetUserRecommendResponse(
            success=True, count=len(user_datas), users=user_datas
        )
        return JsonResponse(
            result.model_dump(),
            status=200,
        )

import json

from django.db.transaction import atomic
from django.http import JsonResponse
from domo_api.http_model import (
    GetAllProjectResponse,
    GetUserDetailInfoResponse,
    GetUserInfoResponse,
    ModifyUserDetailInfoRequest,
    ModifyUserInfoRequest,
    SimpleFailResponse,
    SimpleSuccessResponse,
)
from domo_api.models import Project, S3ResourceReferenceCheck
from domo_api.s3.handler import GeneralHandler, upload_profile_image
from domo_api.tasks import update_github_history
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class Info(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = GetUserInfoResponse(
            success=True,
            email=request.user.email,
            name=request.user.name,
            profile_image_link=request.user.profile_image_link,
        )
        return JsonResponse(response.model_dump(), status=200)

    def put(self, request):
        try:
            request_data = ModifyUserInfoRequest(**request.data)
        except ValidationError:
            return JsonResponse(
                SimpleSuccessResponse(
                    success=False, message="Invalid request."
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

        if request_data.name:
            request.user.name = request_data.name
        if profile_image_link:
            request.user.profile_image_link = profile_image_link
        request.user.save()

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=200,
        )

    def delete(self, request):
        request.user.is_active = False
        request.user.save()

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
        )


class DetailInfo(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        response = GetUserDetailInfoResponse(
            success=True,
            is_public=request.user.is_public,
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
        is_public = request.data.get("email")
        github_link = request.data.get("github_link", None)
        short_description = request.data.get("short_description", None)
        description = request.data.get("description", None)
        description_resource_links = request.data.get(
            "description_resource_links", None
        )
        if description_resource_links:
            description_resource_links = json.loads(description_resource_links)

        data_dict = {
            "is_public": is_public,
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

        # description에 media가 있을경우, validation check가 필요하다.
        # 이후 owner를 지정한다.
        if request_data.description_resource_links:
            s3_handler = GeneralHandler()
            if not s3_handler.check_resource_links(
                request_data.description_resource_links
            ):
                return JsonResponse(
                    SimpleFailResponse(
                        success=False,
                        reason="Invalid request",
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
                    if ref_check_obj.owner == request.user:
                        ref_check_obj.delete()
                        s3_handler.remove_resource(resource_link)

        if request_data.github_link:
            update_github_history.delay(request.user.id, request_data.github_link)

        request.user.is_public = request_data.is_public or request.user.is_public
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

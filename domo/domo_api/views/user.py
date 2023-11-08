from django.http import JsonResponse
from domo_api.http_model import (
    GetAllProjectResponse,
    GetUserDetailInfoResponse,
    GetUserInfoResponse,
    ModifyUserInfoRequest,
    SimpleSuccessResponse,
)
from domo_api.models import Project
from domo_api.s3.handler import upload_profile_image
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
            grade=request.user.grade,
            like=request.user.like,
            rating=request.user.rating,
            provider=request.user.provider,
            last_login=request.user.last_login,
        )
        return JsonResponse(response.model_dump(), status=200)


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

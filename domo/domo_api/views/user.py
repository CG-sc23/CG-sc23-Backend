from django.http import JsonResponse
from domo_api.http_model import (
    GetAllProjectResponse,
    GetUserDetailInfoResponse,
    GetUserInfoResponse,
    SimpleSuccessResponse,
)
from domo_api.models import Project
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView


class Info(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        response = GetUserInfoResponse(
            success=True,
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

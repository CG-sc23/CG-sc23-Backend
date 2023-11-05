import io

from django.http import JsonResponse
from domo_api.http_model import (
    GetAllProjectResponse,
    GetUserInfoResponse,
    ModifyUserInfoRequest,
    SimpleFailResponse,
    SimpleSuccessResponse,
)
from domo_api.models import Project
from domo_api.s3.profile import ProfileHandler
from PIL import Image
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView


class Info(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        response = GetUserInfoResponse(
            success=True,
            email=request.user.email,
            name=request.user.name,
            has_profile_image=request.user.has_profile_image,
            is_public=request.user.is_public,
            github_link=request.user.github_link,
            short_description=request.user.short_description,
            grade=request.user.grade,
            like=request.user.like,
            rating=request.user.rating,
            provider=request.user.provider,
            last_login=request.user.last_login,
        )
        return JsonResponse(response.model_dump(), status=200)

    def put(self, request):
        name = request.data.get("name", None)
        github_link = request.data.get("github_link", None)
        short_description = request.data.get("short_description", None)
        is_public = request.data.get("is_public", None)

        data_dict = {
            "name": name,
            "github_link": github_link,
            "short_description": short_description,
            "is_public": is_public,
        }

        # validate input
        try:
            request_data = ModifyUserInfoRequest(**data_dict)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        # If Upload profile image to S3 first
        profile_upload_success = False
        profile_handler = ProfileHandler()
        if "profile_image" in request.FILES:
            # Convert image to JPEG
            uploaded_image = Image.open(request.FILES["profile_image"])
            output_image_io = io.BytesIO()
            uploaded_image.convert("RGB").save(
                output_image_io, format="JPEG", quality=90
            )

            converted_image_file = io.BytesIO(output_image_io.getvalue())

            profile_upload_success = profile_handler.upload_image(
                request_data.email, converted_image_file
            )
            if not profile_upload_success:
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="Error uploading profile image."
                    ).model_dump(),
                    status=500,
                )
            request.user.has_profile_image = True

        request.user.name = (
            request_data.name if request_data.name else request.user.name
        )
        request.user.github_link = (
            request_data.github_link
            if request_data.github_link
            else request.user.github_link
        )
        request.user.short_description = (
            request_data.short_description
            if request_data.short_description
            else request.user.short_description
        )
        request.user.is_public = (
            request_data.is_public if request_data.is_public else request.user.is_public
        )
        request.user.save()

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
        )

    def delete(self, request):
        request.user.is_active = False
        request.user.save()

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
        )


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

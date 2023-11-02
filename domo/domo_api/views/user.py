import io

from django.http import JsonResponse
from domo_api.http_model import (
    ModifyUserInfoRequest,
    SimpleFailResponse,
    SimpleSuccessResponse,
)
from domo_api.s3.profile import ProfileHandler
from PIL import Image
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView


class Info(APIView):
    authentication_classes = [TokenAuthentication]

    def put(self, request):
        name = request.data.get("name", None)
        github_link = request.data.get("github_link", None)
        short_description = request.data.get("short_description", None)

        data_dict = {
            "name": name,
            "github_link": github_link,
            "short_description": short_description,
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

        request.user.name = request_data.name
        request.user.github_link = request_data.github_link
        request.user.short_description = request_data.short_description
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

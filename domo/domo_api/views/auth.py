import io

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as PasswordValidationError
from django.http import JsonResponse
from domo_api.http_model import (
    SignInRequest,
    SignInResponse,
    SignUpRequest,
    SimpleFailResponse,
    SimpleSuccessResponse,
)
from domo_api.models import User
from domo_api.s3.profile import ProfileHandler
from PIL import Image
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView


class SignUp(APIView):
    def post(self, request):
        request_data_origin = {
            k: v[0] if isinstance(v, list) else v for k, v in request.data.lists()
        }
        # validate input
        try:
            request_data = SignUpRequest(**request_data_origin)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        if User.objects.filter(email=request_data.email).exists():
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User with this email already exists"
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

        try:
            validate_password(request_data.password)
        except PasswordValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Password is too weak."
                ).model_dump(),
                status=400,
            )

        # Create user
        try:
            User.objects.create_user(
                email=request_data.email,
                password=request_data.password,
                name=request_data.name,
                has_profile_image=profile_upload_success,
                github_link=request_data.github_link
                if request_data.github_link
                else None,
                short_description=request_data.short_description
                if request_data.short_description
                else None,
                description=request_data.description
                if request_data.description
                else None,
            )
        except:
            if profile_upload_success:
                profile_handler.delete_directory(request_data.email)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating user"
                ).model_dump(),
                status=500,
            )
        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=201,
        )


class SignIn(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            auth_info = SignInRequest(email=email, password=password)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )
        user = authenticate(email=auth_info.email, password=auth_info.password)
        if user:
            Token.objects.filter(user=user).delete()
            token, _ = Token.objects.get_or_create(user=user)
            response_data = SignInResponse(success=True, token=token.key)
            return JsonResponse(response_data.model_dump(), status=200)
        else:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Email or Password is incorrect."
                ).model_dump(),
                status=401,
            )


class SignOut(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        Token.objects.filter(key=request.auth).delete()
        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
        )

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
    SocialSignUpRequest,
)
from domo_api.models import User
from domo_api.s3.profile import ProfileHandler
from PIL import Image
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView


class SocialSignUp(APIView):
    def post(self, request):
        email = request.data.get("email")
        name = request.data.get("name")
        provider = request.data.get("provider")
        pre_access_token = request.data.get("pre_access_token")
        github_link = request.data.get("github_link", None)
        short_description = request.data.get("short_description", None)
        description = request.data.get("description", None)

        data_dict = {
            "email": email,
            "name": name,
            "provider": provider,
            "pre_access_token": pre_access_token,
            "github_link": github_link,
            "short_description": short_description,
            "description": description,
        }

        # validate input
        try:
            request_data = SocialSignUpRequest(**data_dict)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        if not User.objects.filter(email=request_data.email).exists():
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User with this email not exists."
                ).model_dump(),
                status=400,
            )

        user = User.objects.get(email=request_data.email)
        if user.name != "NOT REGISTERED":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User with this email already registered."
                ).model_dump(),
                status=400,
            )
        if user.pre_access_token != request_data.pre_access_token:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Authentication Failed. (pre_access_token)"
                ).model_dump(),
                status=401,
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

        # Create user
        try:
            user.name = request_data.name
            user.has_profile_image = profile_upload_success
            user.github_link = (
                request_data.github_link if request_data.github_link else None
            )
            user.short_description = (
                request_data.short_description
                if request_data.short_description
                else None
            )
            user.description = (
                request_data.description if request_data.description else None
            )
            user.save()
        except:
            if profile_upload_success:
                profile_handler.delete_directory(request_data.email)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating user."
                ).model_dump(),
                status=500,
            )
        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=201,
        )


class SignUp(APIView):
    def post(self, request):
        email = request.data.get("email")
        name = request.data.get("name")
        password = request.data.get("password")
        github_link = request.data.get("github_link", None)
        short_description = request.data.get("short_description", None)
        description = request.data.get("description", None)

        data_dict = {
            "email": email,
            "name": name,
            "password": password,
            "github_link": github_link,
            "short_description": short_description,
            "description": description,
        }

        # validate input
        try:
            request_data = SignUpRequest(**data_dict)
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
                    success=False, reason="User with this email already exists."
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
                provider="our",
            )
        except:
            if profile_upload_success:
                profile_handler.delete_directory(request_data.email)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating user."
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

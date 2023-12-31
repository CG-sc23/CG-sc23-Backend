import logging
import secrets
from datetime import datetime, timezone

import domo_base.settings.base
from auths.http_model import (
    EmailVerifyConfirmRequest,
    EmailVerifyRequest,
    PasswordResetCheckRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    SignInRequest,
    SignInResponse,
    SignUpRequest,
    SocialSignUpRequest,
)
from auths.models import PasswordResetToken, SignUpEmailVerifyToken
from common.const import ReturnCode
from common.http_model import SimpleFailResponse, SimpleSuccessResponse
from common.s3.handler import upload_profile_image
from common.tasks import update_github_history
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string
from external_histories.models import GithubStatus
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.models import User


class SocialSignUp(APIView):
    def post(self, request):
        name = request.data.get("name")
        pre_access_token = request.data.get("pre_access_token")
        github_link = request.data.get("github_link", None)
        short_description = request.data.get("short_description", None)

        data_dict = {
            "name": name,
            "pre_access_token": pre_access_token,
            "github_link": github_link,
            "short_description": short_description,
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

        if not User.objects.filter(pre_access_token=pre_access_token).exists():
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User not pre-registered."
                ).model_dump(),
                status=400,
            )

        user = User.objects.get(pre_access_token=pre_access_token)
        if user.name != "NOT REGISTERED":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User is already registered."
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

        # If profile image exists, upload to S3 first
        profile_image_link = None
        if "profile_image" in request.FILES:
            profile_image_link = upload_profile_image(
                user, request.FILES["profile_image"]
            )
            # This is a JsonResponse for Exception
            if isinstance(profile_image_link, JsonResponse):
                return profile_image_link
            user.profile_image_updated_at = datetime.now(tz=timezone.utc)

        # Create user
        try:
            user.name = request_data.name
            user.profile_image_link = profile_image_link
            user.github_link = request_data.github_link or None
            user.short_description = request_data.short_description or None
            user.save()
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating user."
                ).model_dump(),
                status=500,
            )
        if request_data.github_link:
            GithubStatus.objects.create(
                user_id=user.id,
                status=ReturnCode.GITHUB_STATUS_IN_PROGRESS,
                last_update=datetime.now(tz=timezone.utc),
            )
            update_github_history.delay(user.id, user.github_link)

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

        data_dict = {
            "email": email,
            "name": name,
            "password": password,
            "github_link": github_link,
            "short_description": short_description,
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

        try:
            user_check = User.objects.get(email=request_data.email)

            if user_check.name != "NOT REGISTERED":
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="User with this email already exists."
                    ).model_dump(),
                    status=400,
                )

        except User.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User didn't verify email yet."
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
            user_check.profile_image_updated_at = datetime.now(tz=timezone.utc)

        # Create user
        try:
            user_check.name = request_data.name
            user_check.profile_image_link = profile_image_link
            user_check.github_link = request_data.github_link or None
            user_check.short_description = request_data.short_description or None
            user_check.provider = "our"
            user_check.set_password(request_data.password)
            user_check.save()
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating user."
                ).model_dump(),
                status=500,
            )
        if request_data.github_link:
            GithubStatus.objects.create(
                user_id=user_check.id,
                status=ReturnCode.GITHUB_STATUS_IN_PROGRESS,
                last_update=datetime.now(tz=timezone.utc),
            )
            update_github_history.delay(user_check.id, user_check.github_link)

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        Token.objects.filter(key=request.auth).delete()
        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
        )


class PasswordChange(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid current password."
                ).model_dump(),
                status=401,
            )

        user.set_password(new_password)
        user.save()
        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=200,
        )


class PasswordReset(APIView):
    def post(self, request):
        email = request.data.get("email")

        try:
            request_data = PasswordResetRequest(email=email)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            user = User.objects.get(email=request_data.email)
            if user.provider != "our":
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="User is not registered with email."
                    ).model_dump(),
                    status=400,
                )
            token = secrets.token_urlsafe(10)
            if PasswordResetToken.objects.filter(user=user).exists():
                PasswordResetToken.objects.filter(user=user).delete()
            PasswordResetToken.objects.create(
                user=user, token=token, created_at=datetime.now(tz=timezone.utc)
            )
            context = {
                "current_user": user,
                "username": user.name,
                "email": user.email,
                "token": token,
            }
            email_html_message = render_to_string(
                "templates/password_reset_email.html", context
            )
            send_mail(
                subject="Password Reset for DOMO",
                message="",
                from_email=domo_base.settings.base.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
                html_message=email_html_message,
            )
            return JsonResponse(
                SimpleSuccessResponse(success=True).model_dump(),
                status=200,
            )

        except User.DoesNotExist:
            return JsonResponse(
                SimpleSuccessResponse(success=True).model_dump(),
                status=200,
            )
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Failed to send email."
                ).model_dump(),
                status=500,
            )


class PasswordResetCheck(APIView):
    def get(self, request):
        email = request.GET.get("email")
        token = request.GET.get("token")

        try:
            request_data = PasswordResetCheckRequest(email=email, token=token)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            password_reset_token = PasswordResetToken.objects.get(
                user__email__iexact=request_data.email
            )

            if password_reset_token.token != request_data.token:
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="Invalid token."
                    ).model_dump(),
                    status=401,
                )
            # 토큰 유효 시간 == 10분
            if (
                datetime.now(tz=timezone.utc) - password_reset_token.created_at
            ).total_seconds() > 600:
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="Token expired."
                    ).model_dump(),
                    status=401,
                )
            return JsonResponse(
                SimpleSuccessResponse(success=True).model_dump(),
                status=200,
            )
        except PasswordResetToken.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(success=False, reason="Invalid token.").model_dump(),
                status=401,
            )


class PasswordResetConfirm(APIView):
    def put(self, request):
        email = request.data.get("email")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        try:
            request_data = PasswordResetConfirmRequest(
                email=email, token=token, new_password=new_password
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            password_reset_token = PasswordResetToken.objects.get(
                user__email__iexact=request_data.email
            )
            if password_reset_token.token != request_data.token:
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="Invalid token."
                    ).model_dump(),
                    status=401,
                )
            user = User.objects.get(email=request_data.email)
            user.set_password(request_data.new_password)
            user.save()

            PasswordResetToken.objects.filter(user=user).delete()
            return JsonResponse(
                SimpleSuccessResponse(success=True).model_dump(),
                status=200,
            )
        except PasswordResetToken.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(success=False, reason="Invalid token.").model_dump(),
                status=401,
            )


class SignUpEmailVerify(APIView):
    def post(self, request):
        email = request.data.get("email")

        try:
            request_data = EmailVerifyRequest(email=email)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        # 유저가 존재하면, 이메일 보내지 말고 200
        if User.objects.filter(email=request_data.email).exists():
            return JsonResponse(
                SimpleSuccessResponse(success=True).model_dump(),
                status=200,
            )

        token = secrets.token_urlsafe(10)
        if SignUpEmailVerifyToken.objects.filter(email=request_data.email).exists():
            SignUpEmailVerifyToken.objects.filter(email=request_data.email).delete()
        SignUpEmailVerifyToken.objects.create(
            email=request_data.email,
            token=token,
            created_at=datetime.now(tz=timezone.utc),
        )

        try:
            context = {
                "email": request_data.email,
                "token": token,
            }
            email_html_message = render_to_string(
                "templates/sign_up_verify_email.html", context
            )
            send_mail(
                subject="Verify Email account for DOMO",
                message="",
                from_email=domo_base.settings.base.DEFAULT_FROM_EMAIL,
                recipient_list=[request_data.email],
                fail_silently=False,
                html_message=email_html_message,
            )
            return JsonResponse(
                SimpleSuccessResponse(success=True).model_dump(),
                status=200,
            )

        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Failed to send email."
                ).model_dump(),
                status=500,
            )


class SignUpEmailVerifyConfirm(APIView):
    def get(self, request):
        email = request.GET.get("email")
        token = request.GET.get("token")

        try:
            request_data = EmailVerifyConfirmRequest(email=email, token=token)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            email_verify_token = SignUpEmailVerifyToken.objects.get(
                email=request_data.email
            )
            if email_verify_token.token != request_data.token:
                return JsonResponse(
                    SimpleFailResponse(
                        success=False,
                        reason="Invalid token.",
                    ).model_dump(),
                    status=401,
                )
            # 토큰 유효 시간 == 10분
            if (
                datetime.now(tz=timezone.utc) - email_verify_token.created_at
            ).total_seconds() > 600:
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="Token expired."
                    ).model_dump(),
                    status=401,
                )

            email_verify_token.delete()

            User.objects.create(
                email=email,
                name="NOT REGISTERED",
                created_at=datetime.now(tz=timezone.utc),
                provider="our",
            )

            return JsonResponse(
                SimpleSuccessResponse(success=True).model_dump(),
                status=200,
            )
        except SignUpEmailVerifyToken.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False,
                    reason="Invalid token.",
                ).model_dump(),
                status=401,
            )

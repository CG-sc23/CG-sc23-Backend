from django.contrib.auth import authenticate
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from domo_api.http_model import (
    SignInRequest,
    SignInResponse,
    SignUpRequest,
    SimpleFailResponse,
    SimpleSuccessResponse,
)
from domo_api.models import User
from domo_base import settings
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class SignUp(APIView):
    def post(self, request):
        # validate input
        try:
            request_data = SignUpRequest(**request.data)
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
        # Create user
        try:
            User.objects.create_user(
                email=request_data.email,
                password=request_data.password,
                name=request_data.name,
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
        except Exception as e:
            print(e)
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
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )


class SignOut(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        request.auth.delete()
        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
        )

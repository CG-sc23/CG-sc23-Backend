from django.contrib.auth import authenticate
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from domo_api.http_model import (
    SignInRequest,
    SignInResponse,
    SimpleFailResponse,
    SimpleSuccessResponse,
)
from domo_api.models import Token
from domo_base import settings
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class SignUp(APIView):
    raise NotImplementedError


class Signin(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            auth_info = SignInRequest(email=email, password=password)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Email or Password is invalid"
                ).model_dump_json(),
                status=400,
            )
        user = authenticate(username=auth_info.email, password=auth_info.password)
        if user:
            Token.objects.filter(user=user).delete()
            token, _ = Token.objects.get_or_create(user=user)
            response_data = SignInResponse(success=True, token=token.key)
            return JsonResponse(response_data.model_dump_json(), status=200)
        else:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Email or Password is invalid"
                ).model_dump_json(),
                status=400,
            )


class SignOut(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        request.auth.delete()
        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump_json(),
        )

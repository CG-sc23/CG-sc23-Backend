import secrets
from datetime import datetime, timezone

import requests
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from ..http_model import (
    SimpleFailResponse,
    SocialPreSignUpResponse,
    SocialSignInResponse,
)
from ..models import User


class Google(APIView):
    def post(self, request):
        access_token = request.data.get("access_token")
        email_req = requests.get(
            f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
        )
        email_req_status = email_req.status_code

        if email_req_status != 200:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Failed to get email."
                ).model_dump(),
                status=400,
            )

        email_req_json = email_req.json()
        email = email_req_json.get("email")

        try:
            user = User.objects.get(email=email)
            if user.provider != "google":
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="No matching social type."
                    ).model_dump(),
                    status=400,
                )
            if user.name == "NOT REGISTERED":
                user.delete()
                raise User.DoesNotExist

            # 성공하면, DOMO 로그인에 사용할 토큰 생성 및 response.
            Token.objects.filter(user=user).delete()
            token, _ = Token.objects.get_or_create(user=user)
            response_data = SocialSignInResponse(
                success=True,
                is_user=True,
                token=token.key,
            )
            return JsonResponse(response_data.model_dump(), status=200)

        except User.DoesNotExist:
            # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 새로운 회원가입 준비
            pre_access_token = secrets.token_urlsafe(32)
            response_data = SocialPreSignUpResponse(
                success=True,
                is_user=False,
                pre_access_token=pre_access_token,
            )
            # Create user
            try:
                User.objects.create(
                    email=email,
                    name="NOT REGISTERED",
                    provider="google",
                    pre_access_token=pre_access_token,
                    created_at=datetime.now(tz=timezone.utc),
                )
            except:
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="Error pre-creating user."
                    ).model_dump(),
                    status=500,
                )
            return JsonResponse(response_data.model_dump(), status=200)


class Kakao(APIView):
    def post(self, request):
        access_token = request.data.get("access_token")

        user_info_req = requests.get(
            f"https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info_req_json = user_info_req.json()
        email = user_info_req_json.get("kakao_account").get("email")

        try:
            user = User.objects.get(email=email)
            if user.provider != "kakao":
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="No matching social type."
                    ).model_dump(),
                    status=400,
                )
            if user.name == "NOT REGISTERED":
                user.delete()
                raise User.DoesNotExist

            # 성공하면, DOMO 로그인에 사용할 토큰 생성 및 response.
            Token.objects.filter(user=user).delete()
            token, _ = Token.objects.get_or_create(user=user)
            response_data = SocialSignInResponse(
                success=True,
                is_user=True,
                token=token.key,
            )
            return JsonResponse(response_data.model_dump(), status=200)

        except User.DoesNotExist:
            # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 새로운 회원가입 준비
            pre_access_token = secrets.token_urlsafe(32)
            response_data = SocialPreSignUpResponse(
                success=True,
                is_user=False,
                pre_access_token=pre_access_token,
            )
            # Create user
            try:
                User.objects.create(
                    email=email,
                    name="NOT REGISTERED",
                    provider="kakao",
                    pre_access_token=pre_access_token,
                    created_at=datetime.now(tz=timezone.utc),
                )
            except:
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="Error pre-creating user."
                    ).model_dump(),
                    status=500,
                )
            return JsonResponse(response_data.model_dump(), status=200)

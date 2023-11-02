import logging
import os
import secrets
from datetime import datetime, timezone

import requests
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from ..const import ReturnCode
from ..http_model import (
    SimpleFailResponse,
    SocialPreSignUpResponse,
    SocialSignInResponse,
)
from ..models import User


def oauth_finish(status):
    if status[0] == ReturnCode.NO_MATCHING_SOCIAL_TYPE:
        return JsonResponse(
            SimpleFailResponse(
                success=False, reason="No matching social type."
            ).model_dump(),
            status=400,
        )
    elif status[0] == ReturnCode.ERROR_PRE_CREATING_USER:
        return JsonResponse(
            SimpleFailResponse(
                success=False, reason="Error pre-creating user."
            ).model_dump(),
            status=500,
        )
    elif status[0] == ReturnCode.SIGN_IN_SUCCESS:
        return JsonResponse(
            status[1].model_dump(),
            status=200,
        )
    elif status[0] == ReturnCode.PRE_SIGN_UP_SUCCESS:
        return JsonResponse(
            status[1].model_dump(),
            status=200,
        )


def sign_in(email, social_type):
    try:
        user = User.objects.get(email=email)
        if user.provider != social_type:
            return ReturnCode.NO_MATCHING_SOCIAL_TYPE, None

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
        return ReturnCode.SIGN_IN_SUCCESS, response_data

    except User.DoesNotExist:
        return pre_sign_up(email, social_type)


def pre_sign_up(email, social_type):
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
            provider=social_type,
            pre_access_token=pre_access_token,
            created_at=datetime.now(tz=timezone.utc),
        )
    except:
        return ReturnCode.ERROR_PRE_CREATING_USER, None

    return ReturnCode.PRE_SIGN_UP_SUCCESS, response_data


class Kakao(APIView):
    def post(self, request):
        code = request.data.get("code")

        client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
        redirect_uri = os.environ.get("SOCIAL_AUTH_REDIRECT_URI")
        access_token_req = requests.post(
            f"https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "code": code,
            },
        )

        if access_token_req.status_code != 200:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Failed to get access_token."
                ).model_dump(),
                status=500,
            )

        access_token_req_json = access_token_req.json()
        access_token = access_token_req_json.get("access_token")

        user_info_req = requests.get(
            f"https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info_req_json = user_info_req.json()
        email = user_info_req_json.get("kakao_account").get("email")

        status = sign_in(email, "kakao")

        response = oauth_finish(status)
        return response


class Naver(APIView):
    def post(self, request):
        code = request.data.get("code")

        client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
        client_secret = os.environ.get("SOCIAL_AUTH_NAVER_SECRET")
        access_token_req = requests.post(
            f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&"
            f"client_id={client_id}&"
            f"client_secret={client_secret}&"
            f"code={code}&state=domomainweb!@"
        )

        if access_token_req.status_code != 200:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Failed to get access_token."
                ).model_dump(),
                status=500,
            )

        access_token_req_json = access_token_req.json()
        access_token = access_token_req_json.get("access_token")

        user_info_req = requests.post(
            f"https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info_req_json = user_info_req.json()
        email = user_info_req_json.get("response").get("email")

        status = sign_in(email, "naver")

        response = oauth_finish(status)
        return response

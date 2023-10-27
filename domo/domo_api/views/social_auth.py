import os
from datetime import datetime, timezone

import requests
from django.http import JsonResponse
from django.shortcuts import redirect
from requests import JSONDecodeError
from rest_framework.authtoken.models import Token

from ..http_model import SignInResponse, SimpleFailResponse, SocialSignUpResponse
from ..models import User

BASE_URL = "https://api.domowebest.com"


class Google:
    CALLBACK_URI = BASE_URL + "/api/auth/v1/social/google/callback/"

    @staticmethod
    def sign_in(request):
        scope = "https://www.googleapis.com/auth/userinfo.email"
        client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        return redirect(
            f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}"
            f"&response_type=code&redirect_uri={Google.CALLBACK_URI}&scope={scope}"
        )

    @staticmethod
    def callback(request):
        client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
        code = request.GET.get("code")

        # 1. 받은 코드로 구글에 access token 요청
        token_req = requests.post(
            f"https://oauth2.googleapis.com/token?client_id={client_id}&"
            f"client_secret={client_secret}&code={code}&"
            f"grant_type=authorization_code&redirect_uri={Google.CALLBACK_URI}"
        )

        ### 1-1. json으로 변환 & 에러 부분 파싱
        token_req_json = token_req.json()
        error = token_req_json.get("error")

        ### 1-2. 에러 발생 시 종료
        if error is not None:
            raise JSONDecodeError(error)

        ### 1-3. 성공 시 access_token 가져오기
        access_token = token_req_json.get("access_token")

        # 2. 가져온 access_token으로 이메일을 구글에 요청
        email_req = requests.get(
            f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
        )
        email_req_status = email_req.status_code

        ### 2-1. 에러 발생 시 400 에러 반환
        if email_req_status != 200:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Failed to get email."
                ).model_dump(),
                status=400,
            )

        ### 2-2. 성공 시 이메일 가져오기
        email_req_json = email_req.json()
        email = email_req_json.get("email")

        # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
        try:
            # 전달받은 이메일로 등록된 유저가 있는지 탐색
            user = User.objects.get(email=email)

            # 있는데 구글계정이 아니어도 에러
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
            response_data = SignInResponse(success=True, token=token.key)
            return JsonResponse(response_data.model_dump(), status=200)

        except User.DoesNotExist:
            # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 새로운 회원가입 준비
            response_data = SocialSignUpResponse(
                success=True,
                email=email,
                pre_access_token=access_token,
                provider="google",
                message="Social sign-up is ready.",
            )
            # Create user
            try:
                User.objects.create(
                    email=email,
                    name="NOT REGISTERED",
                    provider="google",
                    pre_access_token=access_token,
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


class Kakao:
    CALLBACK_URI = BASE_URL + "/api/auth/v1/social/kakao/callback/"

    @staticmethod
    def sign_in(request):
        client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
        return redirect(
            f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}"
            f"&response_type=code&redirect_uri={Kakao.CALLBACK_URI}"
        )

    @staticmethod
    def callback(request):
        client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
        code = request.GET.get("code")

        token_req = requests.post(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&"
            f"client_id={client_id}&code={code}&"
            f"redirect_uri={Kakao.CALLBACK_URI}"
        )
        token_req_json = token_req.json()

        error = token_req_json.get("error")
        if error:
            return JsonResponse(
                SimpleFailResponse(success=False, reason=error).model_dump(), status=500
            )

        access_token = token_req_json.get("access_token")

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

            Token.objects.filter(user=user).delete()
            token, _ = Token.objects.get_or_create(user=user)
            response_data = SignInResponse(success=True, token=token.key)
            return JsonResponse(response_data.model_dump(), status=200)

        except User.DoesNotExist:
            response_data = SocialSignUpResponse(
                success=True,
                email=email,
                pre_access_token=access_token,
                provider="kakao",
                message="Social sign-up is ready.",
            )
            try:
                User.objects.create(
                    email=email,
                    name="NOT REGISTERED",
                    provider="kakao",
                    pre_access_token=access_token,
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

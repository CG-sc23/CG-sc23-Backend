from datetime import datetime, timezone
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User


class SocialAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.kakao_url = reverse("kakao")
        self.naver_url = reverse("naver")

        self.kakao_user = User.objects.create(
            email="test@kakao.com",
            name="test",
            provider="kakao",
            pre_access_token="VALID_PRE_ACCESS_TOKEN",
            created_at=datetime.now(tz=timezone.utc),
        )

        self.naver_user = User.objects.create(
            email="test@naver.com",
            name="test",
            provider="naver",
            pre_access_token="VALID_PRE_ACCESS_TOKEN",
            created_at=datetime.now(tz=timezone.utc),
        )

    def tearDown(self):
        User.objects.all().delete()

    def mocked_requests_post(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        if args[0].startswith("https://openapi.naver.com/v1"):
            return MockResponse({"response": {"email": "test@naver.com"}}, 200)
        else:
            return MockResponse({"access_token": "VALID_ACCESS_TOKEN"}, 200)

    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        if args[0].startswith("https://kapi.kakao.com"):
            return MockResponse({"kakao_account": {"email": "test@kakao.com"}}, 200)
        else:
            return MockResponse(None, 404)

    @patch("auths.views.social_auth.requests.post", side_effect=mocked_requests_post)
    @patch("auths.views.social_auth.requests.get", side_effect=mocked_requests_get)
    def test_kakao_sign_in(self, _, __):
        # Given: 카카오로 회원가입 되어있는 사용자
        # When: 소셜 로그인 요청을 했을 때
        response = self.client.post(
            self.kakao_url,
            {"code": "VALID_CODE"},
        )

        # Then: 로그인이 성공해야 한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertTrue(response.json()["is_user"])
        self.assertTrue(isinstance(response.json()["token"], str))

    @patch("auths.views.social_auth.requests.post", side_effect=mocked_requests_post)
    def test_naver_sign_in(self, _):
        # Given: 네이버로 회원가입 되어있는 사용자
        # When: 소셜 로그인 요청을 했을 때
        response = self.client.post(
            self.naver_url,
            {"code": "VALID_CODE"},
        )

        # Then: 로그인이 성공해야 한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertTrue(response.json()["is_user"])
        self.assertTrue(isinstance(response.json()["token"], str))

    @patch("auths.views.social_auth.requests.post", side_effect=mocked_requests_post)
    @patch("auths.views.social_auth.requests.get", side_effect=mocked_requests_get)
    def test_kakao_pre_sign_up(self, _, __):
        # Given: 카카오로 회원가입 되어있지 않은 사용자
        self.kakao_user.delete()

        # When: 소셜 로그인 요청을 했을 때
        response = self.client.post(
            self.kakao_url,
            {"code": "VALID_CODE"},
        )

        # Then: 사전 회원가입이 성공해야 한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(response.json()["is_user"])
        self.assertTrue(isinstance(response.json()["pre_access_token"], str))

    @patch("auths.views.social_auth.requests.post", side_effect=mocked_requests_post)
    @patch("auths.views.social_auth.requests.get", side_effect=mocked_requests_get)
    def test_naver_pre_sign_up(self, _, __):
        # Given: 네이버로 회원가입 되어있지 않은 사용자
        self.naver_user.delete()

        # When: 소셜 로그인 요청을 했을 때
        response = self.client.post(
            self.naver_url,
            {"code": "VALID_CODE"},
        )

        # Then: 사전 회원가입이 성공해야 한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(response.json()["is_user"])
        self.assertTrue(isinstance(response.json()["pre_access_token"], str))

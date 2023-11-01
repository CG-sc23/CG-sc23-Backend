from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from django.test import TestCase, override_settings
from django.urls import reverse
from domo_api.models import SignUpEmailVerifyToken, User
from rest_framework.test import APIClient


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SignUpEmailVerifyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "test@domo.com"
        self.url_email_verify = reverse("email_verify")
        self.url_email_verify_confirm = reverse("email_verify_confirm")

    def test_send_email_verify_success(self):
        # Given: 유효한 이메일
        # When: 유효한 이메일로 회원가입 요청을 보내면
        response = self.client.post(self.url_email_verify, {"email": self.email})

        # Then: 응답 코드는 200이고, 이메일 인증 토큰이 생성된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            SignUpEmailVerifyToken.objects.filter(email=self.email).exists()
        )

    def test_send_email_verify_but_invalid_email(self):
        # Given: 유효하지 않은 이메일
        # When: 유효하지 않은 이메일로 회원가입 요청을 보내면
        response = self.client.post(self.url_email_verify, {"email": "invaliddomo.com"})

        # Then: 응답 코드는 400이다.
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid request.")

    def test_send_email_verify_but_already_registered_email(self):
        # Given: 이미 가입된 이메일
        User.objects.create_user(
            email=self.email, password="Testpassword123!", name="TestUser"
        )
        # When: 해당 이메일로 회원가입 요청을 보내면
        response = self.client.post(self.url_email_verify, {"email": self.email})

        # Then: 응답 코드는 200이다. 그러나 실제 토큰은 생성되지 않는다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(
            SignUpEmailVerifyToken.objects.filter(email=self.email).exists()
        )

    def test_verify_confirm_valid_token(self):
        # Given: 유효한 회원가입 토큰
        token = SignUpEmailVerifyToken.objects.create(
            email=self.email, created_at=datetime.now(tz=timezone.utc)
        )

        # When: 해당 토큰으로 인증 확인 요청을 보내면
        encoded_params = urlencode({"email": self.email, "token": token.token})
        url = f"{self.url_email_verify_confirm}?{encoded_params}"

        response = self.client.get(url)

        # Then: 응답 코드는 200이다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_verify_confirm_invalid_token(self):
        SignUpEmailVerifyToken.objects.create(
            email=self.email, created_at=datetime.now(tz=timezone.utc)
        )

        # Given: 유효하지 않은 회원가입 토큰
        # When: 해당 토큰으로 인증 확인 요청을 보내면
        encoded_params = urlencode({"email": self.email, "token": "invalidtoken"})
        url = f"{self.url_email_verify_confirm}?{encoded_params}"

        response = self.client.get(url)

        # Then: 응답 코드는 401(유효하지 않은 토큰)이다.
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid token.")

    def test_verify_confirm_no_email_in_token_db(self):
        # Given: 유효하지 않은 비밀번호 재설정 토큰, DB에는 이메일을 가지고 있는 토큰이 없다.
        # When: 해당 토큰으로 비밀번호 재설정 확인 요청을 보내면
        encoded_params = urlencode({"email": self.email, "token": "invalidtoken"})
        url = f"{self.url_email_verify_confirm}?{encoded_params}"

        response = self.client.get(url)

        # Then: 응답 코드는 401(유효하지 않은 토큰)이다.
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid token.")

    def test_verify_confirm_expired_token(self):
        # Given: 11분 전에 생성된 비밀번호 재설정 토큰
        token = SignUpEmailVerifyToken.objects.create(
            email=self.email, created_at=datetime.now(tz=timezone.utc)
        )
        token.created_at = datetime.now(tz=timezone.utc) - timedelta(minutes=11)
        token.save()

        # When: 해당 토큰으로 비밀번호 재설정 확인 요청을 보내면
        encoded_params = urlencode({"email": self.email, "token": token.token})
        url = f"{self.url_email_verify_confirm}?{encoded_params}"

        response = self.client.get(url)

        # Then: 응답 코드는 401(만료된 토큰)이다.
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Token expired.")

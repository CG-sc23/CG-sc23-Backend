from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from django.test import TestCase, override_settings
from django.urls import reverse
from domo_api.models import PasswordResetToken, User
from rest_framework.test import APIClient


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "test@domo.com"
        self.password = "Testpassword123!"
        self.user = User.objects.create_user(
            email=self.email, password=self.password, name="TestUser"
        )
        self.url_password_reset = reverse("password_reset")
        self.url_password_reset_check = reverse("password_reset_check")
        self.url_password_reset_confirm = reverse("password_reset_confirm")

    def test_password_reset_success(self):
        # Given: 유효한 이메일
        # When: 유효한 이메일로 비밀번호 재설정 요청을 보내면
        response = self.client.post(self.url_password_reset, {"email": self.email})

        # Then: 응답 코드는 200이고, 비밀번호 재설정 토큰이 생성된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(PasswordResetToken.objects.filter(user=self.user).exists())

    def test_password_reset_with_provider(self):
        # Given: 소셜 로그인 사용자
        self.user.provider = "google"
        self.user.save()

        # When: 비밀번호 재설정 요청을 보내면
        response = self.client.post(self.url_password_reset, {"email": self.email})

        # Then: 응답 코드는 400이다.
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(
            response.json()["reason"], "User is not registered with email."
        )

    def test_password_reset_invalid_email(self):
        # Given: 유효하지 않은 이메일
        # When: 유효하지 않은 이메일로 비밀번호 재설정 요청을 보내면
        response = self.client.post(
            self.url_password_reset, {"email": "invalid@domo.com"}
        )

        # Then: 응답 코드는 200이다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_password_reset_check_valid_token(self):
        # Given: 유효한 비밀번호 재설정 토큰
        token = PasswordResetToken.objects.create(
            user=self.user, created_at=datetime.now(tz=timezone.utc)
        )

        encoded_params = urlencode({"email": self.email, "token": token.token})
        url = f"{self.url_password_reset_check}?{encoded_params}"

        # When: 해당 토큰으로 비밀번호 재설정 확인 요청을 보내면
        response = self.client.get(url)

        # Then: 응답 코드는 200이다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_password_reset_check_invalid_token(self):
        PasswordResetToken.objects.create(
            user=self.user, created_at=datetime.now(tz=timezone.utc)
        )

        # Given: 유효하지 않은 비밀번호 재설정 토큰
        # When: 해당 토큰으로 비밀번호 재설정 확인 요청을 보내면
        encoded_params = urlencode({"email": self.email, "token": "invalidtoken"})
        url = f"{self.url_password_reset_check}?{encoded_params}"

        response = self.client.get(url)

        # Then: 응답 코드는 401(유효하지 않은 토큰)이다.
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid token.")

    def test_password_reset_check_no_token_in_db(self):
        # Given: 유효하지 않은 비밀번호 재설정 토큰, DB에는 유저를 FK로 갖는 토큰이 없다.
        # When: 해당 토큰으로 비밀번호 재설정 확인 요청을 보내면
        encoded_params = urlencode({"email": self.email, "token": "invalidtoken"})
        url = f"{self.url_password_reset_check}?{encoded_params}"

        response = self.client.get(url)

        # Then: 응답 코드는 401(유효하지 않은 토큰)이다.
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid token.")

    def test_password_reset_check_expired_token(self):
        # Given: 11분 전에 생성된 비밀번호 재설정 토큰
        token = PasswordResetToken.objects.create(
            user=self.user, created_at=datetime.now(tz=timezone.utc)
        )
        token.created_at = datetime.now(tz=timezone.utc) - timedelta(minutes=11)
        token.save()

        # When: 해당 토큰으로 비밀번호 재설정 확인 요청을 보내면
        encoded_params = urlencode({"email": self.email, "token": token.token})
        url = f"{self.url_password_reset_check}?{encoded_params}"

        response = self.client.get(url)

        # Then: 응답 코드는 401(만료된 토큰)이다.
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Token expired.")

    def test_password_reset_confirm_success(self):
        # Given: 유효한 비밀번호 재설정 토큰
        token = PasswordResetToken.objects.create(
            user=self.user, created_at=datetime.now(tz=timezone.utc)
        )

        # When: 새 비밀번호와 함께 비밀번호 재설정 확인 요청을 보낸다.
        response = self.client.post(
            self.url_password_reset_confirm,
            {
                "email": self.email,
                "token": token.token,
                "new_password": "NewPassword123!",
            },
        )

        # Then: 응답 코드는 200이고, 사용자의 비밀번호가 성공적으로 변경된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123!"))

from django.urls import reverse
from domo_api.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase


class PasswordChangeTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_password_change = reverse("password_change")
        self.url_sign_in = reverse("sign_in")
        self.email = "test@example.com"
        self.password = "VAL1DP@sSW0Rd"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            name="춘식이",
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_password_change_success(self):
        # Given: 유효한 토큰으로 로그인 되어 있을 때, 기존 비밀번호, 새 비밀번호
        # When: 비밀번호 재설정 요청을 보내면
        response = self.client.put(
            self.url_password_change,
            {
                "current_password": self.password,
                "new_password": "NewPassword123!",
            },
        )

        # Then: 응답 코드는 200이고, 비밀번호가 변경된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertTrue(
            User.objects.get(email=self.email).check_password("NewPassword123!")
        )

    def test_password_change_wrong_current_password(self):
        # Given: 유효한 토큰으로 로그인 되어 있을 때, 틀린 기존 비밀번호, 새 비밀번호
        # When: 비밀번호 재설정 요청을 보내면
        response = self.client.put(
            self.url_password_change,
            {
                "current_password": "WrongPassword",
                "new_password": "NewPassword123!",
            },
        )

        # Then: 응답 코드는 401이고, 비밀번호가 변경되지 않는다.
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid current password.")
        self.assertFalse(
            User.objects.get(email=self.email).check_password("NewPassword123!")
        )

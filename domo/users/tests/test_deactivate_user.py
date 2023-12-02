from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class DeactivateUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.created_at = datetime.now(tz=timezone.utc)
        self.user = User.objects.create(
            email="test@email.com",
            password="testpassword",
            name="test",
            created_at=self.created_at,
            provider="our",
        )

        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

        self.url_user_info = reverse("user_info")

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success_deactivate(self):
        # Given: 사용자
        # When: 사용자가 회원탈퇴를 요청했을 때
        url = self.url_user_info
        response = self.client.delete(url)
        # Then: 응답 코드는 200이다. 그리고 사용자는 비활성화된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

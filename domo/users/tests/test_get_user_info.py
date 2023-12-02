from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class GetUserInfoTest(TestCase):
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
        self.url_user_detail_info = reverse("user_detail_info")
        self.url_user_public_detail_info = reverse(
            "user_public_detail_info", args=[self.user.id]
        )

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success_simple_info(self):
        # Given: 사용자
        # When: 사용자 자신의 기본 정보를 조회할 때
        url = self.url_user_info
        response = self.client.get(url)

        expected_response = {
            "success": True,
            "user_id": self.user.id,
            "email": self.user.email,
            "name": self.user.name,
            "profile_image_link": self.user.profile_image_link,
            "profile_image_updated_at": self.user.profile_image_updated_at,
            "provider": self.user.provider,
        }

        # Then: 응답 코드는 200이고 사용자의 기본 정보를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json(), expected_response)

    def test_success_detail_info(self):
        # Given: 사용자
        # When: 사용자 자신의 상세 정보를 조회할 때
        url = self.url_user_detail_info
        response = self.client.get(url)

        expected_response = {
            "success": True,
            "github_link": self.user.github_link,
            "short_description": self.user.short_description,
            "description": self.user.description,
            "description_resource_links": self.user.description_resource_links,
            "grade": self.user.grade,
            "like": self.user.like,
            "rating": self.user.rating,
            "provider": self.user.provider,
        }

        # Then: 응답 코드는 200이고 사용자의 상세 정보를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json(), expected_response)

    def test_success_public_info(self):
        # Given: 사용자
        # When: 다른 사용자가 특정 사용자의 상세 정보를 조회할 때
        url = self.url_user_public_detail_info
        response = self.client.get(url)

        expected_response = {
            "success": True,
            "email": self.user.email,
            "name": self.user.name,
            "profile_image_link": self.user.profile_image_link,
            "profile_image_updated_at": self.user.profile_image_updated_at,
            "github_link": self.user.github_link,
            "short_description": self.user.short_description,
            "description": self.user.description,
            "description_resource_links": self.user.description_resource_links,
            "grade": self.user.grade,
            "like": self.user.like,
            "rating": self.user.rating,
        }

        # Then: 응답 코드는 200이고 사용자의 상세 정보를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json(), expected_response)

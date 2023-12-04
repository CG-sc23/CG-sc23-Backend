from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class RecommendProjectTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.created_at = datetime.now(tz=timezone.utc)

        self.user_owner = User.objects.create(
            email="test1@email.com",
            password="testpassword",
            name="test1",
            created_at=self.created_at,
        )

        self.user_not_in_project = User.objects.create(
            email="test2@email.com",
            password="testpassword",
            name="test2",
            created_at=self.created_at,
        )

        self.token = Token.objects.create(user=self.user_not_in_project)
        self.api_authentication()

        self.project = self.user_owner.project_set.create(
            title="Test Project",
            created_at=self.created_at,
            due_date=self.created_at,
            status="IN_PROGRESS",
        )
        self.project_member = ProjectMember.objects.create(
            project=self.project,
            user=self.user_owner,
            role="OWNER",
            created_at=datetime.now(tz=timezone.utc),
        )

        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"

        self.expected_response = {
            "success": True,
            "count": 1,
            "projects": [
                {
                    "id": self.project.id,
                    "title": "Test Project",
                    "status": "IN_PROGRESS",
                    "created_at": self.time_check_v,
                    "due_date": self.time_check_v,
                    "thumbnail_image": self.project.thumbnail_image,
                    "short_description": self.project.short_description,
                    "members": [
                        {
                            "email": self.user_owner.email,
                            "id": self.user_owner.id,
                            "name": self.user_owner.name,
                            "profile_image_link": None,
                            "profile_image_updated_at": None,
                        }
                    ],
                }
            ],
        }

        self.url_recommend_project = reverse("project_recommend")

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 사용자가 속하지 않은 프로젝트가 존재
        # When: 사용자가 프로젝트 추천을 요청할 때
        url = self.url_recommend_project
        response = self.client.get(url)

        # Then: 응답 코드는 200이고 요청한 프로젝트의 정보를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.expected_response)

    def test_success_public(self):
        # Given: 로그인 하지 않은 클라이언트
        self.client.credentials()
        # When: 프로젝트 추천을 요청할 때
        url = self.url_recommend_project
        response = self.client.get(url)

        # Then: 응답 코드는 200이고 요청한 프로젝트의 정보를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.expected_response)

from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from projects.models import ProjectMember
from rest_framework.test import APIClient
from users.models import User


class GetProjectInfoTest(TestCase):
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
        self.project = self.user.project_set.create(
            title="test",
            created_at=self.created_at,
            due_date=self.created_at,
        )
        ProjectMember.objects.create(
            user=self.user,
            project=self.project,
            role="OWNER",
            created_at=self.created_at,
        )
        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"
        self.url_project_info = reverse("user_project_info", args=[self.user.id])

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 프로젝트
        # When: 어떤 사용자가 특정 사용자가 참여 중인 프로젝트 정보를 조회할 때
        url = self.url_project_info
        response = self.client.get(url)

        expected_response = {
            "success": True,
            "count": 1,
            "projects": [
                {
                    "project": {
                        "id": self.project.id,
                        "owner": {
                            "id": self.user.id,
                            "name": self.user.name,
                            "email": self.user.email,
                            "profile_image_link": self.user.profile_image_link,
                            "profile_image_updated_at": self.user.profile_image_updated_at,
                        },
                        "status": self.project.status,
                        "title": self.project.title,
                        "short_description": self.project.short_description,
                        "description": self.project.description,
                        "description_resource_links": self.project.description_resource_links,
                        "created_at": self.time_check_v,
                        "due_date": self.time_check_v,
                        "thumbnail_image": self.project.thumbnail_image,
                        "members": [
                            {
                                "id": self.user.id,
                                "name": self.user.name,
                                "email": self.user.email,
                                "profile_image_link": self.user.profile_image_link,
                                "profile_image_updated_at": self.user.profile_image_updated_at,
                            }
                        ],
                    },
                }
            ],
        }

        # Then: 응답 코드는 200이고 사용자가 속해있는 프로젝트 정보들을 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json(), expected_response)

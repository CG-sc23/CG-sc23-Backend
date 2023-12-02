from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class CreateMilestoneTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.created_at = datetime.now(tz=timezone.utc)

        self.user = User.objects.create(
            email="test@email.com",
            password="testpassword",
            name="test",
            created_at=self.created_at,
        )
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

        self.project = self.user.project_set.create(
            title="Test Project",
            created_at=self.created_at,
        )
        self.project_member = ProjectMember.objects.create(
            project=self.project,
            user=self.user,
            role="OWNER",
            created_at=datetime.now(tz=timezone.utc),
        )
        self.url_create_milestone = reverse("milestone_info", args=[self.project.id])

        self.milestone_payload = {
            "subject": "Test Subject",
            "tags": '["Test Tag1", "Test Tag2"]',
            "due_date": self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        }

        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"
        self.due_date_check_v = self.created_at.replace(
            hour=14, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.due_date_check_v = self.due_date_check_v[:-3] + "Z"

        self.expected_response = {
            "success": True,
            "id": 1,
            "subject": "Test Subject",
            "tags": ["Test Tag1", "Test Tag2"],
            "status": "IN_PROGRESS",
            "created_at": self.time_check_v,
            "due_date": self.due_date_check_v,
        }

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 프로젝트와 관리자 (OWNER or MANAGER)
        # When: 관리자가 마일스톤을 생성할 때
        url = self.url_create_milestone
        response = self.client.post(url, self.milestone_payload)
        response.json()["created_at"] = self.time_check_v
        response.json()["id"] = 1
        # Then: 응답 코드는 200이고 생성된 마일스톤의 정보를 반환한다.
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.expected_response)

    def test_permission_error(self):
        # Given: 프로젝트 참가자 (관리자가 아닌)
        self.project_member.role = "MEMBER"
        self.project_member.save()

        # When: 참가자가 마일스톤을 생성하려고 시도할 때
        url = self.url_create_milestone
        response = self.client.post(url)

        # Then: 응답 코드는 403이다.
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "User must OWNER or MANAGER")

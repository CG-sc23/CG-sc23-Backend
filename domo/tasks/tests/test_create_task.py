from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

from common.s3.handler import GeneralHandler
from django.urls import reverse
from milestones.models import Milestone
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from task_groups.models import TaskGroup
from users.models import User


class CreateTaskTest(TestCase):
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

        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"

        self.milestone = Milestone.objects.create(
            project=self.project,
            created_by=self.user,
            subject="Test Subject",
            tags=["Test Tag1", "Test Tag2"],
            created_at=self.created_at,
            due_date=self.created_at,
        )

        self.task_group = TaskGroup.objects.create(
            milestone=self.milestone,
            created_by=self.user,
            title="Test Task Group",
            tags=None,
            status="READY",
            created_at=self.created_at,
            due_date=self.created_at,
        )

        self.url_task = reverse("task_info", args=[self.task_group.id])

        self.task_payload = {
            "title": "Test Task",
            "description": "Test Description",
            "description_resource_links": '["Link1", "Link2"]',
            "tags": '["Tag1", "Tag2"]',
        }

        self.expected_response = {
            "success": True,
            "id": 1,
            "title": "Test Task",
            "description": "Test Description",
            "description_resource_links": ["Link1", "Link2"],
            "created_at": self.time_check_v,
            "tags": ["Tag1", "Tag2"],
            "is_public": True,
        }

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    @patch.object(GeneralHandler, "check_resource_links")
    def test_success(self, mock_s3):
        # Given: 태스크 그룹
        # When: 사용자가 태스크 그룹에 속할 태스크를 생성할 때
        mock_s3.return_value = True
        url = self.url_task
        response = self.client.post(url, self.task_payload)

        response.json()["id"] = 1
        response.json()["created_at"] = self.time_check_v

        # Then: 응답 코드는 201이고 생성된 태스크의 정보를 반환한다.
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.expected_response)

    def test_permission_error(self):
        # Given: 인증되지 않은 사용자
        self.client.credentials()
        # When: 태스크를 생성하려고 시도할 때
        url = self.url_task
        response = self.client.post(url, self.task_payload)

        # Then: 응답 코드는 403이다.
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Permission error")

    def test_not_found(self):
        # Given: 태스크 그룹
        # When: 사용자가 없는 태스크 그룹에 대한 태스크을 생성하려고 시도할 때
        url = reverse("task_info", args=[self.task_group.id + 1])
        response = self.client.post(url, self.task_payload)

        # Then: 응답 코드는 404이다.
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Task group not found.")

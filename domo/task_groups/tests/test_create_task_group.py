from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from milestones.models import Milestone
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class CreateTaskGroupTest(TestCase):
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

        self.url_task_group_url = reverse("task_group_info", args=[self.milestone.id])

        self.task_group_payload = {
            "title": "Test Task Group",
            "due_date": self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        }

        self.expected_response = {
            "success": True,
            "id": 1,
            "status": "READY",
            "title": "Test Task Group",
            "created_at": self.time_check_v,
            "due_date": self.time_check_v,
        }

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 마일스톤
        # When: 사용자가 마일스톤에 속할 태스크 그룹을 생성할 때
        url = self.url_task_group_url
        response = self.client.post(url, self.task_group_payload)

        response.json()["id"] = 1
        response.json()["created_at"] = self.time_check_v
        response.json()["due_date"] = self.time_check_v

        # Then: 응답 코드는 201이고 생성된 태스크 그룹의 정보를 반환한다.
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.expected_response)

    def test_permission_error(self):
        # Given: 프로젝트 참가자 (관리자가 아닌)
        self.project_member.role = "MEMBER"
        self.project_member.save()

        # When: 참가자가 마일스톤을 생성하려고 시도할 때
        url = self.url_task_group_url
        response = self.client.post(url, self.task_group_payload)

        # Then: 응답 코드는 403이다.
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "User must OWNER or MANAGER")

    def test_not_found(self):
        # Given: 프로젝트, 마일스톤
        # When: 사용자가 없는 마일스톤에 대한 태스크 그룹을 생성하려고 시도할 때
        url = reverse("task_group_info", args=[self.milestone.id + 1])
        response = self.client.post(url, self.task_group_payload)

        # Then: 응답 코드는 404이다.
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Milestone not found")

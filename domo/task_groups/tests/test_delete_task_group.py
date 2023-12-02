from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from milestones.models import Milestone
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from task_groups.models import TaskGroup
from users.models import User


class DeleteTaskGroupTest(TestCase):
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

        self.url_task_group = reverse("task_group_info", args=[self.task_group.id])

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 태스크 그룹
        # When: 사용자가 태스크 그룹을 삭제할 때
        url = self.url_task_group
        response = self.client.delete(url)

        # Then: 응답 코드는 200이고 태스크 그룹을 삭제한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_not_found(self):
        # Given: 태스크 그룹
        # When: 사용자가 없는 태스크 그룹을 삭제하려고 할 때
        url = reverse("task_group_info", args=[self.task_group.id + 1])
        response = self.client.delete(url)

        # Then: 응답 코드는 404이다.
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Task group not found")

    def test_permission_error(self):
        # Given: 프로젝트 참가자 (관리자가 아닌)
        self.project_member.role = "MEMBER"
        self.project_member.save()

        # When: 참가자가 마일스톤을 삭제하려고 시도할 때
        url = self.url_task_group
        response = self.client.delete(url)

        # Then: 응답 코드는 403이다.
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "User must OWNER or MANAGER")

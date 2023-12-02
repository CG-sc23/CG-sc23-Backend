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
from tasks.models import Task
from users.models import User


class DeleteTaskTest(TestCase):
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

        self.task = Task.objects.create(
            task_group=self.task_group,
            owner=self.user,
            title="Test Task",
            description="Test Description",
            description_resource_links=["Link1", "Link2"],
            tags=["Tag1", "Tag2"],
            created_at=self.created_at,
            is_public=True,
        )

        self.user.s3resourcereferencecheck_set.create(
            resource_link="Link1",
        )
        self.user.s3resourcereferencecheck_set.create(
            resource_link="Link2",
        )

        self.url_task = reverse("task_info", args=[self.task.id])

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    @patch.object(GeneralHandler, "remove_resource")
    def test_success(self, _):
        # Given: 태스크
        # When: 사용자가 태스크를 삭제할 때
        url = self.url_task
        response = self.client.delete(url)

        # Then: 응답 코드는 200이고 태스크를 삭제한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_not_found(self):
        # Given: 태스크
        # When: 사용자가 없는 태스크를 삭제하려고 할 때
        url = reverse("task_info", args=[self.task.id + 1])
        response = self.client.delete(url)

        # Then: 응답 코드는 404이다.
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Can't find Task.")

    def test_permission_error(self):
        # Given: 인증되지 않은 사용자
        self.client.credentials()

        # When: 태스크를 삭제하려고 시도할 때
        url = self.url_task
        response = self.client.delete(url)

        # Then: 응답 코드는 403이다.
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Permission error")

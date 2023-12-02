from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from milestones.models import Milestone
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from task_groups.models import TaskGroup
from tasks.models import Task
from users.models import User


class ModifyTaskTest(TestCase):
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

        self.url_task = reverse("task_info", args=[self.task.id])

        self.expected_response = {
            "success": True,
            "id": self.task.id,
            "title": "MODIFIED Test Task",
            "description": self.task.description,
            "description_resource_links": self.task.description_resource_links,
            "created_at": self.time_check_v,
            "tags": self.task.tags,
            "is_public": True,
        }

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 태스크
        # When: 사용자가 태스크 정보를 수정할 때
        url = self.url_task
        response = self.client.put(url, data={"title": "MODIFIED Test Task"})

        # Then: 응답 코드는 201이고 수정된 태스크 정보를 반환한다.
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json(), self.expected_response)

    def test_not_found(self):
        # Given: 태스크
        # When: 사용자가 없는 태스크에 대해 수정 시도할 때
        url = reverse("task_info", args=[self.task.id + 1])
        response = self.client.put(url)

        # Then: 응답 코드는 404이다.
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Can't find Task.")

from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from milestones.models import Milestone
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class GetMilestoneTest(TestCase):
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

        task_group = self.milestone.taskgroup_set.create(
            title="Test Task Group",
            created_by=self.user,
            created_at=self.created_at,
        )

        task_group.task_set.create(
            title="Test Task",
            owner=self.user,
            created_at=self.created_at,
        )

        self.url_get_milestone = reverse("milestone_info", args=[self.milestone.id])

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 프로젝트, 마일스톱, 태스크 그룹, 태스크
        # When: 사용자가 마일스톤 정보를 확인할 때
        url = self.url_get_milestone
        response = self.client.get(url)

        # Then: 응답 코드는 200이고 프로젝트 및 마일스톤과 이에 속한 태스크 그룹, 태스크의 정보를 반환한다.
        self.assertEqual(response.status_code, 200)

    def test_not_found(self):
        # Given: 프로젝트, 마일스톱, 태스크 그룹
        # When: 사용자가 없는 마일스톤 정보를 요청했을 때
        url = reverse("milestone_info", args=[self.milestone.id + 1])
        response = self.client.get(url)

        # Then: 응답 코드는 404이다.
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Milestone not found")

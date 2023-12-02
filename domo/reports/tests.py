from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from milestones.models import Milestone
from projects.models import ProjectMember
from reports.models import Report
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class CreateReportTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.created_at = datetime.now(tz=timezone.utc)

        self.user = User.objects.create(
            email="test@email.com",
            password="testpassword",
            name="test",
            created_at=self.created_at,
        )
        self.user_reporter = User.objects.create(
            email="test2@email.com",
            password="testpassword",
            name="test2",
            created_at=self.created_at,
        )

        self.token = Token.objects.create(user=self.user_reporter)
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

        self.task = task_group.task_set.create(
            title="Test Task",
            owner=self.user,
            created_at=self.created_at,
        )

        self.url_create_report = reverse("report_info", args=[self.task.id])

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 프로젝트, 마일스톱, 태스크 그룹, 태스크
        # When: 사용자가 태스크 정보를 신고하면
        url = self.url_create_report
        response = self.client.post(url, {"title": "Test Title"})

        # Then: 응답 코드는 201이고 관리자가 확인할 수 있도록 내용이 DB에 저장된다.
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["success"], True)
        self.assertEqual(Report.objects.all().count(), 1)

    def test_not_found(self):
        # Given: 프로젝트, 마일스톱, 태스크 그룹, 태스크
        # When: 사용자가 없는 태스크 정보를 신고하면
        url = reverse("report_info", args=[self.task.id + 1])
        response = self.client.post(url, {"title": "Test Title"})

        # Then: 응답 코드는 404이다.
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(response.json()["reason"], "Can't find task.")

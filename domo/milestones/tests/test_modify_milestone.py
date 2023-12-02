from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from milestones.models import Milestone
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class ModifyMilestoneTest(TestCase):
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
        self.url_modify_milestone = reverse("milestone_info", args=[self.milestone.id])

        self.milestone_payload = {
            "subject": "MODIFIED Test Subject",
        }

        self.expected_response = {
            "success": True,
            "id": self.milestone.id,
            "subject": "MODIFIED Test Subject",
            "tags": ["Test Tag1", "Test Tag2"],
            "status": "IN_PROGRESS",
            "created_at": self.time_check_v,
            "due_date": self.time_check_v,
        }

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 프로젝트와 관리자 (OWNER or MANAGER)
        # When: 관리자가 마일스톤을 수정할 때
        url = self.url_modify_milestone
        response = self.client.put(url, self.milestone_payload)

        # Then: 응답 코드는 201이고 수정된 마일스톤의 정보를 반환한다.
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.expected_response)

    def test_permission_error(self):
        # Given: 프로젝트 참가자 (관리자가 아닌)
        self.project_member.role = "MEMBER"
        self.project_member.save()

        # When: 참가자가 마일스톤을 생성하려고 시도할 때
        url = self.url_modify_milestone
        response = self.client.put(url, self.milestone_payload)

        # Then: 응답 코드는 403이다.
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "User must OWNER or MANAGER")

    def test_not_found(self):
        # Given: 프로젝트, 마일스톱, 태스크 그룹
        # When: 사용자가 없는 마일스톤 정보를 수정하려고 할 때
        url = reverse("milestone_info", args=[self.milestone.id + 1])
        response = self.client.put(url, self.milestone_payload)

        # Then: 응답 코드는 404이다.
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Milestone not found")

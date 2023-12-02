from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class InviteProjectTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.created_at = datetime.now(tz=timezone.utc)

        self.user_inviter = User.objects.create(
            email="test@email.com",
            password="testpassword",
            name="test",
            created_at=self.created_at,
        )
        self.user_invitee = User.objects.create(
            email="test2@email.com",
            password="testpassword",
            name="test",
            created_at=self.created_at,
        )
        self.token = Token.objects.create(user=self.user_inviter)
        self.api_authentication()

        self.project = self.user_inviter.project_set.create(
            title="Test Project",
            short_description="Test short description",
            description="Test description",
            description_resource_links=["Link1", "Link2"],
            created_at=self.created_at,
            due_date=self.created_at,
            thumbnail_image="thumbnail image link",
            status="IN_PROGRESS",
        )
        self.project_member = ProjectMember.objects.create(
            project=self.project,
            user=self.user_inviter,
            role="OWNER",
            created_at=datetime.now(tz=timezone.utc),
        )

        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"

        self.invite_payload = {
            "project_id": self.project.id,
            "invitee_emails": f'["{self.user_invitee.email}"]',
        }

        self.expected_response = {
            "result": [
                {
                    "invitee_email": self.user_invitee.email,
                    "success": True,
                    "reason": None,
                }
            ]
        }

        self.url_invite_project = reverse("project_invite")

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 초대할 사용자, 초대받을 사용자, 프로젝트
        # When: 사용자가 프로젝트에 다른 사용자를 초대할 때
        url = self.url_invite_project
        response = self.client.post(url, self.invite_payload)

        # Then: 응답 코드는 200이고 각 사용자에 대한 초대 성공 여부를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.expected_response)

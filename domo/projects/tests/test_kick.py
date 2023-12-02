from datetime import datetime, timezone
from unittest import TestCase
from urllib.parse import urlencode

from django.urls import reverse
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class KickTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.created_at = datetime.now(tz=timezone.utc)

        self.user_owner = User.objects.create(
            email="test@email.com",
            password="testpassword",
            name="test",
            created_at=self.created_at,
        )
        self.user_member = User.objects.create(
            email="test2@email.com",
            password="testpassword",
            name="test",
            created_at=self.created_at,
        )
        self.token = Token.objects.create(user=self.user_owner)
        self.api_authentication()

        self.project = self.user_owner.project_set.create(
            title="Test Project",
            short_description="Test short description",
            description="Test description",
            description_resource_links=["Link1", "Link2"],
            created_at=self.created_at,
            due_date=self.created_at,
            thumbnail_image="thumbnail image link",
            status="IN_PROGRESS",
        )
        self.project_owner_obj = ProjectMember.objects.create(
            project=self.project,
            user=self.user_owner,
            role="OWNER",
            created_at=datetime.now(tz=timezone.utc),
        )
        self.project_member_obj = ProjectMember.objects.create(
            project=self.project,
            user=self.user_member,
            role="MEMBER",
            created_at=datetime.now(tz=timezone.utc),
        )

        self.url_kick = reverse("project_kick", args=[self.project.id])

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 프로젝트 생성자, 프로젝트 멤버
        # When: 프로젝트 생성자가 프로젝트 멤버를 내보낼 때
        url = self.url_kick
        encoded_params = urlencode({"user_email": self.user_member.email})
        url = f"{url}?{encoded_params}"
        response = self.client.delete(url)

        # Then: 응답 코드는 200이고 멤버는 프로젝트에서 내보내진다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(ProjectMember.objects.count(), 1)

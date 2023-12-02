from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from projects.models import ProjectJoinRequest, ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class ReplyJoinRequestTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.created_at = datetime.now(tz=timezone.utc)

        self.user_owner = User.objects.create(
            email="test@email.com",
            password="testpassword",
            name="test",
            created_at=self.created_at,
        )
        self.user_not_member = User.objects.create(
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

        self.url_reply_join = reverse("project_join_request_reply")

        self.project_join_request = ProjectJoinRequest.objects.create(
            project=self.project,
            user=self.user_not_member,
            message="Hello",
            created_at=self.created_at,
        )

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success_accept(self):
        # Given: 프로젝트 생성자, 초대 요청
        # When: 관리자가 초대 요청을 수락하면
        url = self.url_reply_join
        response = self.client.post(
            url, {"join_request_id": self.project_join_request.id, "accept": True}
        )

        # Then: 응답 코드는 200이고 사용자가 프로젝트에 추가된다. 요청은 삭제된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(ProjectMember.objects.count(), 2)
        self.assertEqual(ProjectJoinRequest.objects.count(), 0)

    def test_success_deny(self):
        # Given: 프로젝트 생성자, 초대 요청
        # When: 관리자가 초대 요청을 거절하면
        url = self.url_reply_join
        response = self.client.post(
            url, {"join_request_id": self.project_join_request.id, "accept": False}
        )

        # Then: 응답 코드는 200이고 사용자가 프로젝트에 추가되지 않고 요청은 삭제된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(ProjectMember.objects.count(), 1)
        self.assertEqual(ProjectJoinRequest.objects.count(), 0)

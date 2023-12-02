from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from projects.models import ProjectJoinRequest, ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class MakeJoinRequestTest(TestCase):
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
        self.token = Token.objects.create(user=self.user_not_member)
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

        self.url_make_join = reverse("project_join_request", args=[self.project.id])

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 프로젝트 생성자, 프로젝트에 아직 속하지 않은 사용자
        # When: 사용자가 프로젝트에 가입 요청을 보내면
        url = self.url_make_join
        response = self.client.post(url, {"message": "Hello"})

        # Then: 응답 코드는 200이고 가입 요청이 생성된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(ProjectJoinRequest.objects.count(), 1)


class MakeJoinGetTest(TestCase):
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

        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"

        self.url_make_join = reverse("project_join_request", args=[self.project.id])

        self.project_join_request = ProjectJoinRequest.objects.create(
            project=self.project,
            user=self.user_not_member,
            message="Hello",
            created_at=self.created_at,
        )

        self.expected_response = {
            "success": True,
            "result": [
                {
                    "id": self.project_join_request.id,
                    "user": {
                        "id": self.user_not_member.id,
                        "name": self.user_not_member.name,
                        "email": self.user_not_member.email,
                        "profile_image_link": None,
                        "profile_image_updated_at": None,
                    },
                    "message": "Hello",
                    "created_at": self.time_check_v,
                }
            ],
        }

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 프로젝트 생성자, 초대 요청
        # When: 관리자가 초대 요청을 확인하면
        url = self.url_make_join
        response = self.client.get(url)

        # Then: 응답 코드는 200이고 가입 요청이 반환된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json(), self.expected_response)

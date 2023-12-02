from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

from common.s3.handler import GeneralHandler
from django.urls import reverse
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class CreateProjectTest(TestCase):
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

        self.project_payload = {
            "title": "Test Project",
            "short_description": "Test short description",
            "description": "Test description",
            "description_resource_links": '["Link1", "Link2"]',
            "due_date": self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "thumbnail_image": "thumbnail image link",
        }

        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"
        self.due_date_check_v = self.created_at.replace(
            hour=14, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.due_date_check_v = self.due_date_check_v[:-3] + "Z"

        self.expected_response = {
            "success": True,
            "id": 1,
            "status": "IN_PROGRESS",
            "title": "Test Project",
            "short_description": "Test short description",
            "description": "Test description",
            "description_resource_links": ["Link1", "Link2"],
            "created_at": self.time_check_v,
            "due_date": self.due_date_check_v,
            "thumbnail_image": "thumbnail image link",
        }

        self.url_create_project = reverse("project_info")

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    @patch.object(GeneralHandler, "check_resource_links")
    def test_success(self, mock_s3_handler):
        # Given: 사용자
        # When: 사용자가 프로젝트를 생성할 때
        mock_s3_handler.return_value = True
        url = self.url_create_project
        response = self.client.post(url, self.project_payload)
        response.json()["created_at"] = self.time_check_v
        response.json()["id"] = 1

        # Then: 응답 코드는 201이고 생성된 프로젝트의 정보를 반환한다.
        # ProjectMember 테이블에도 관계가 생성된다.
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.expected_response)
        self.assertEqual(self.user.project_set.count(), 1)
        self.assertEqual(self.user.projectmember_set.count(), 1)


class ModifyProjectTest(TestCase):
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
            short_description="Test short description",
            description="Test description",
            description_resource_links=["Link1", "Link2"],
            created_at=self.created_at,
            due_date=self.created_at,
            thumbnail_image="thumbnail image link",
            status="IN_PROGRESS",
        )
        self.user.s3resourcereferencecheck_set.create(
            resource_link="Link1",
        )
        self.user.s3resourcereferencecheck_set.create(
            resource_link="Link2",
        )
        self.project_member = ProjectMember.objects.create(
            project=self.project,
            user=self.user,
            role="OWNER",
            created_at=datetime.now(tz=timezone.utc),
        )

        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"

        self.project_payload = {
            "title": "MODIFIED Test Project",
            "description_resource_links": '["Link2", "Link3"]',
        }

        self.expected_response = {
            "success": True,
            "id": self.project.id,
            "status": "IN_PROGRESS",
            "title": "MODIFIED Test Project",
            "short_description": "Test short description",
            "description": "Test description",
            "description_resource_links": ["Link2", "Link3"],
            "created_at": self.time_check_v,
            "due_date": self.time_check_v,
            "thumbnail_image": "thumbnail image link",
        }

        self.url_modify_project = reverse("project_info_id", args=[self.project.id])

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    @patch.object(GeneralHandler, "check_resource_links")
    @patch.object(GeneralHandler, "remove_resource")
    def test_success(self, _, mock_s3_handler):
        # Given: 사용자
        # When: 사용자가 프로젝트를 수정할 때
        mock_s3_handler.return_value = True
        url = self.url_modify_project
        response = self.client.put(url, self.project_payload)

        # Then: 응답 코드는 200이고 수정된 프로젝트의 정보를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.expected_response)


class GetProjectTest(TestCase):
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
            user=self.user,
            role="OWNER",
            created_at=datetime.now(tz=timezone.utc),
        )

        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"

        self.project_payload = {
            "title": "MODIFIED Test Project",
        }

        self.expected_response = {
            "success": True,
            "owner": {
                "email": self.user.email,
                "id": self.user.id,
                "name": self.user.name,
                "profile_image_link": None,
                "profile_image_updated_at": None,
            },
            "id": self.project.id,
            "status": "IN_PROGRESS",
            "title": "Test Project",
            "short_description": "Test short description",
            "description": "Test description",
            "description_resource_links": ["Link1", "Link2"],
            "created_at": self.time_check_v,
            "due_date": self.time_check_v,
            "thumbnail_image": "thumbnail image link",
            "milestones": [],
            "members": [
                {
                    "email": self.user.email,
                    "id": self.user.id,
                    "name": self.user.name,
                    "profile_image_link": None,
                    "profile_image_updated_at": None,
                }
            ],
            "permission": "OWNER",
        }

        self.url_get_project = reverse("project_info", args=[self.project.id])

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: 프로젝트
        # When: 사용자가 프로젝트 정보를 요청할 때
        url = self.url_get_project
        response = self.client.get(url)

        # Then: 응답 코드는 200이고 요청한 프로젝트의 정보를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.expected_response)


class DeleteProjectTest(TestCase):
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
            user=self.user,
            role="OWNER",
            created_at=datetime.now(tz=timezone.utc),
        )
        self.user.s3resourcereferencecheck_set.create(
            resource_link="Link1",
        )
        self.user.s3resourcereferencecheck_set.create(
            resource_link="Link2",
        )
        self.user.s3resourcereferencecheck_set.create(
            resource_link="thumbnail image link",
        )

        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"

        self.url_delete_project = reverse("project_info_id", args=[self.project.id])

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    @patch.object(GeneralHandler, "remove_resource")
    def test_success(self, _):
        # Given: 프로젝트
        # When: 사용자가 프로젝트를 삭제할 때
        url = self.url_delete_project
        response = self.client.delete(url)

        # Then: 응답 코드는 200이고 프로젝트는 삭제된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(self.user.project_set.count(), 0)

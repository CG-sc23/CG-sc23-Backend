from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

from common.gpt import MilestoneGPT
from django.urls import reverse
from projects.models import ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class MakeMilestoneByGptTest(TestCase):
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
        self.owner_obj = ProjectMember.objects.create(
            project=self.project,
            user=self.user,
            role="OWNER",
            created_at=self.created_at,
        )

        self.url_gpt = reverse("project_make_milestone_gpt", args=[self.project.id])

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    @patch.object(MilestoneGPT, "get_response")
    def test_success(self, mock_gpt):
        # Given: 프로젝트
        # When: 사용자가 프로젝트에 적절한 마일스톤을 찾기 위해 GPT를 요청하면
        mock_gpt.return_value = '{"title": "some title", "tags": ["tag1", "tag2"]}'
        url = self.url_gpt
        response = self.client.get(url)

        expected_response = {
            "success": True,
            "title": "some title",
            "tags": ["tag1", "tag2"],
        }

        # Then: 응답 코드는 200이고 GPT가 추천한 정보가 반환된다.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

    @patch.object(MilestoneGPT, "get_response")
    def test_fail_with_gpt_problem(self, mock_gpt):
        # Given: 프로젝트
        # When: 사용자가 프로젝트에 적절한 마일스톤을 찾기 위해 GPT를 요청하면
        mock_gpt.return_value = "CANT_UNDERSTAND"
        url = self.url_gpt
        response = self.client.get(url)

        expected_response = {
            "success": False,
            "reason": "GPT response is invalid.",
        }

        # Then: 응답 코드는 200이고 GPT가 추천한 정보가 반환된다.
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), expected_response)

    def test_fail_with_member(self):
        # Given: 프로젝트, 멤버
        self.owner_obj.role = "MEMBER"
        self.owner_obj.save()
        # When: 프로젝트 멤버가 (관리자 X) GPT를 요청하면
        url = self.url_gpt

        # Then: 권한 예외가 발생하고 응답 코드는 403이다.
        with self.assertRaises(PermissionError):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

    def test_fail_with_no_project(self):
        # Given: 프로젝트, 멤버
        # When: 프로젝트 멤버가 잘못된 project_id로 GPT를 요청하면
        url = self.url_gpt.replace(str(self.project.id), "9999")

        # Then: 응답 코드는 404.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Project does not exist.")

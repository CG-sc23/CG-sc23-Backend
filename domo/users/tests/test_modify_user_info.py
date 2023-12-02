from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

from common.s3.handler import GeneralHandler
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class ModifyUserInfoTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.created_at = datetime.now(tz=timezone.utc)
        self.user = User.objects.create(
            email="test@email.com",
            password="testpassword",
            name="test",
            created_at=self.created_at,
            description="test description",
            description_resource_links=["Link1", "Link2"],
            provider="our",
        )
        self.user.s3resourcereferencecheck_set.create(
            resource_link="Link1",
        )
        self.user.s3resourcereferencecheck_set.create(
            resource_link="Link2",
        )

        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

        self.url_user_detail_info = reverse("user_detail_info")

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    @patch.object(GeneralHandler, "remove_resource")
    @patch.object(GeneralHandler, "check_resource_links")
    def test_success_modify_info(self, mock_check_resource_links, _):
        # Given: 사용자
        # When: 사용자 자신의 상세 정보를 수정할 때
        mock_check_resource_links.return_value = True
        url = self.url_user_detail_info
        response = self.client.put(
            url,
            {
                "profile_image_link": "Link",
                "description_resource_links": '["Link2", "Link3"]',
            },
        )
        # Then: 응답 코드는 200이다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

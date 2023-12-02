from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import urlencode

from common.s3.handler import GeneralHandler
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class PreSignedUrlTest(TestCase):
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

        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"

        self.url_pre_signed_url = reverse("pre_signed_url", args=["test.jpeg"])

        self.aws_return_value = [
            0,
            {
                "url": "test_aws_url",
                "fields": {
                    "key": "test.jpeg",
                    "x-amz-algorithm": "test_algorithm",
                    "x-amz-credential": "test_credential",
                    "x-amz-date": "test_date",
                    "policy": "test_policy",
                    "x-amz-signature": "test_signature",
                },
            },
        ]

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    @patch.object(GeneralHandler, "create_presigned_url")
    def test_success_get_url(self, mock_s3):
        # Given: 사용자, 적절한 파일 이름
        # When: 사용자가 s3에 업로드 할 파일에 대한 presigned-url을 요청했을 때
        mock_s3.return_value = self.aws_return_value
        encoded_params = urlencode({"type": "resource"})
        url = f"{self.url_pre_signed_url}?{encoded_params}"
        response = self.client.get(url)

        expected_response = {
            "success": True,
            "url": "test_aws_urltest.jpeg",
            "aws_response": self.aws_return_value[1],
        }
        # Then: 응답 코드는 200이고 AWS의 응답과 함께 추후 필요한 정보를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

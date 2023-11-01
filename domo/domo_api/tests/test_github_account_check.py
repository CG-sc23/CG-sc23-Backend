from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase


class GithubAccountCheckTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_github_account_check = reverse("github_account_check")
        self.account = "test"

    @patch("requests.get")
    def test_github_account_check_success(self, mock_get):
        class MockResponse:
            def __init__(self, status_code):
                self.status_code = status_code

        mock_get.return_value = MockResponse(200)
        # Given: 유효한 github 계정
        # When: 유효한 계정인지 조회할 때
        response = self.client.post(
            self.url_github_account_check,
            {
                "account": self.account,
            },
        )

        # Then: 응답 코드는 200
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    @patch("requests.get")
    def test_github_account_check_with_not_exist_account(self, mock_get):
        class MockResponse:
            def __init__(self, status_code):
                self.status_code = status_code

        mock_get.return_value = MockResponse(404)
        # Given: 유효하지 않은 github 계정
        # When: 유효한 계정인지 조회할 때
        response = self.client.post(
            self.url_github_account_check,
            {
                "account": self.account,
            },
        )

        # Then: 응답 코드는 404
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Can't find github account.")

    def test_github_account_check_with_invalid_request(self):
        # Given: Request Type Error
        # When: 유효한 계정인지 조회할 때
        response = self.client.post(
            self.url_github_account_check,
            {
                "accoun": 100,
            },
        )

        # Then: 응답 코드는 400.
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid request.")

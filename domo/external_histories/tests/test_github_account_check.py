from unittest import TestCase
from unittest.mock import patch
from urllib.parse import urlencode

from django.urls import reverse
from rest_framework.test import APIClient


class GithubAccountCheckTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_github_account_check = reverse("github_account_check")
        self.github_link = "github.com/test"

    @patch("requests.get")
    def test_github_account_check_success(self, mock_get):
        class MockResponse:
            def __init__(self, status_code):
                self.status_code = status_code

        mock_get.return_value = MockResponse(200)
        # Given: 유효한 github 계정
        # When: 유효한 계정인지 조회할 때
        encoded_params = urlencode({"github_link": self.github_link})
        url = f"{self.url_github_account_check}?{encoded_params}"

        response = self.client.get(url)

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
        encoded_params = urlencode({"github_link": self.github_link})
        url = f"{self.url_github_account_check}?{encoded_params}"

        response = self.client.get(url)

        # Then: 응답 코드는 404
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Can't find github account.")

    def test_pydantic_check_fail(self):
        # Given: Request Type Error
        # When: 유효한 계정인지 조회할 때
        encoded_params = urlencode({"github_lin": 100})
        url = f"{self.url_github_account_check}?{encoded_params}"

        response = self.client.get(url)

        # Then: 응답 코드는 400.
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid request.")

    def test_user_input_invalid_that_not_github_link(self):
        # Given: 유효하지 않은 사용자 입력 (github.com/ 이 없는 경우)
        # When: 유효한 계정인지 조회할 때
        encoded_params = urlencode({"github_link": "https://githu.com/test"})
        url = f"{self.url_github_account_check}?{encoded_params}"

        response = self.client.get(url)

        # Then: 응답 코드는 400이다.
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid request.")

    def test_user_input_invalid_that_github_link_is_literally_github_com(self):
        # Given: 유효하지 않은 사용자 입력 (github.com/ 만 있는 경우)
        # When: 유효한 계정인지 조회할 때
        encoded_params = urlencode({"github_link": "https://github.com"})
        url = f"{self.url_github_account_check}?{encoded_params}"

        response = self.client.get(url)

        # Then: 응답 코드는 400이다.
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid request.")

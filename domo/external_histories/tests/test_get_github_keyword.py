from datetime import datetime, timezone
from unittest import TestCase

from common.const import ReturnCode
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class GetGithubKeywordTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_github_keyword = reverse("get_github_keyword")
        self.last_update = datetime.now(tz=timezone.utc)
        self.user = User.objects.create_user(
            email="test@email.com", password="testpassword", name="test"
        )
        self.github_status = self.user.githubstatus_set.create(
            status="COMPLETE", last_update=self.last_update
        )
        self.github_keyword = self.user.userkeyword_set.create(
            keyword="react", count=100
        )
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: github update status가 COMPLETE인 사용자
        # When: 사용자의 keyword를 조회할 때
        url = self.url_github_keyword
        response = self.client.get(url)

        # Then: 응답 코드는 200이고 사용자의 keyword를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(
            response.json()["keywords"][self.github_keyword.keyword],
            self.github_keyword.count,
        )

    def test_not_exist_github_status(self):
        # Given: github update status가 존재하지 않는 사용자
        self.github_status.delete()
        # When: 사용자의 keyword를 조회할 때
        url = self.url_github_keyword
        response = self.client.get(url)

        # Then: 응답 코드는 404이다.
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Github status Not Found")

    def test_github_status_is_in_progress(self):
        # Given: github update가 진행중인 사용자
        self.github_status.status = ReturnCode.GITHUB_STATUS_IN_PROGRESS
        self.github_status.save()
        # When: 사용자의 keyword를 조회할 때
        url = self.url_github_keyword
        response = self.client.get(url)

        # Then: 응답 코드는 503이다.
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Github status is in progress")

    def test_github_status_is_failed(self):
        # Given: github update가 실패한 사용자
        self.github_status.status = ReturnCode.GITHUB_STATUS_FAILED
        self.github_status.save()
        # When: 사용자의 keyword를 조회할 때
        url = self.url_github_keyword
        response = self.client.get(url)

        # Then: 응답 코드는 503이다.
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Github status failed to update")


class GetPublicGithubStackTest(GetGithubKeywordTest):
    def setUp(self):
        super().setUp()
        self.url_github_keyword = reverse(
            "get_public_github_keyword", args=[self.user.id]
        )

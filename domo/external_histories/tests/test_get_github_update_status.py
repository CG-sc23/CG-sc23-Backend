from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User


class GetGithubUpdateStatusTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.last_update = datetime.now(tz=timezone.utc)
        self.user = User.objects.create_user(
            email="test@email.com", password="testpassword", name="test"
        )
        self.github_status = self.user.githubstatus_set.create(
            status="COMPLETE", last_update=self.last_update
        )

        self.url_github_account_check = reverse(
            "get_github_update_status", args=[self.user.id]
        )

    def tearDown(self):
        User.objects.all().delete()

    def test_success(self):
        # Given: github update status가 존재하는 사용자
        # When: 사용자의 github update status를 조회할 때
        url = f"{self.url_github_account_check}"
        response = self.client.get(url)

        # Then: 응답 코드는 200이고 사용자의 github update status를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["status"], self.github_status.status)

        time_check_v = self.github_status.last_update.strftime("%Y-%m-%dT%H:%M:%S.%f")
        time_check_v = time_check_v[:-3] + "Z"
        self.assertEqual(response.json()["last_update"], time_check_v)

    def test_not_exist_github_status(self):
        # Given: github update status가 존재하지 않는 사용자
        self.github_status.delete()
        # When: 사용자의 github update status를 조회할 때
        url = f"{self.url_github_account_check}"
        response = self.client.get(url)

        # Then: 응답 코드는 404이다.
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Github status Not Found")

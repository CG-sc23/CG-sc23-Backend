from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

from common.const import ReturnCode
from django.urls import reverse
from external_histories.models import GithubStatus
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class UpdateManualGithubTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_github_update = reverse("github_manual_update")
        self.last_update = datetime.now(tz=timezone.utc)
        self.user = User.objects.create_user(
            email="test@email.com",
            password="testpassword",
            name="test",
            github_link="https://github.com/test",
        )
        self.github_status = self.user.githubstatus_set.create(
            status="COMPLETE", last_update=self.last_update
        )
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def tearDown(self):
        User.objects.all().delete()

    @patch("common.tasks.update_github_history.delay")
    def test_success(self, mock_github_delay):
        # Given: github update status가 COMPLETE인 사용자
        # When: 사용자가 github update를 요청할 때
        url = self.url_github_update
        response = self.client.post(url)

        # Then: 응답 코드는 202이고 github update status가 IN_PROGRESS로 변경된다.
        # 그리고 github update를 수행하는 task가 실행된다.
        self.assertEqual(response.status_code, 202)
        self.assertTrue(response.json()["success"])
        self.github_status.refresh_from_db()
        self.assertEqual(
            self.github_status.status, ReturnCode.GITHUB_STATUS_IN_PROGRESS
        )
        mock_github_delay.assert_called_once_with(self.user.id, self.user.github_link)

    @patch("common.tasks.update_github_history.delay")
    def test_success_first_time(self, mock_github_delay):
        # Given: github update status가 존재하지 않는 사용자
        self.github_status.delete()
        # (회원가입 때 github link가 없었고, 이후 github link를 추가한 경우 + 주기적 업데이트가 돌기 전 사용자의 요청)
        # When: 사용자가 github update를 요청할 때
        url = self.url_github_update
        response = self.client.post(url)

        # Then: 응답 코드는 202이고 github update status가 IN_PROGRESS인 상태로 생성된다.
        # 그리고 github update를 수행하는 task가 실행된다.
        self.assertEqual(response.status_code, 202)
        self.assertTrue(response.json()["success"])
        github_status = GithubStatus.objects.get(user_id=self.user.id)
        self.assertEqual(github_status.status, ReturnCode.GITHUB_STATUS_IN_PROGRESS)
        mock_github_delay.assert_called_once_with(self.user.id, self.user.github_link)

    def test_not_exist_github_url(self):
        # Given: github url이 존재하지 않는 사용자
        self.user.github_link = None
        self.user.save()

        # When: 사용자가 github update를 요청할 때
        url = self.url_github_update
        response = self.client.post(url)

        # Then: 응답 코드는 400이다.
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "You don't have github link.")

    def test_github_status_is_in_progress(self):
        # Given: github update가 진행중인 사용자
        self.github_status.status = ReturnCode.GITHUB_STATUS_IN_PROGRESS
        self.github_status.save()

        # When: 사용자가 github update를 요청할 때
        url = self.url_github_update
        response = self.client.post(url)

        # Then: 응답 코드는 503이다.
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Github status is in progress")

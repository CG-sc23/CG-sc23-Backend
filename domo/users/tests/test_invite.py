from datetime import datetime, timezone
from unittest import TestCase

from django.urls import reverse
from projects.models import ProjectInvite, ProjectMember
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User


class Invite(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.created_at = datetime.now(tz=timezone.utc)
        self.user_inviter = User.objects.create(
            email="test@email.com",
            password="testpassword",
            name="test",
            created_at=self.created_at,
        )
        self.user_invitee = User.objects.create(
            email="test2@email.com",
            password="testpassword",
            name="test",
            created_at=self.created_at,
        )
        self.token = Token.objects.create(user=self.user_inviter)
        self.api_authentication()

        self.project = self.user_inviter.project_set.create(
            title="test",
            created_at=self.created_at,
        )
        ProjectMember.objects.create(
            project=self.project,
            user=self.user_inviter,
            role="OWNER",
            created_at=self.created_at,
        )
        ProjectInvite.objects.create(
            inviter=self.user_inviter,
            invitee=self.user_invitee,
            project=self.project,
            created_at=self.created_at,
        )
        self.time_check_v = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.time_check_v = self.time_check_v[:-3] + "Z"

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")


class InviterTest(Invite):
    def setUp(self):
        super().setUp()
        self.url_user_inviter = reverse("user_inviter")

    def tearDown(self):
        User.objects.all().delete()

    def test_success_invite_info(self):
        # Given: 사용자
        # When: 사용자가 자신이 초대한 사용자의 정보를 조회할 때
        url = self.url_user_inviter
        response = self.client.get(url)

        expected_response = {
            "success": True,
            "result": [
                {
                    "project_id": self.project.id,
                    "invitee_email": self.user_invitee.email,
                    "created_at": self.time_check_v,
                }
            ],
        }

        # Then: 응답 코드는 200이고 해당 정보를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json(), expected_response)


class InviteeTest(Invite):
    def setUp(self):
        super().setUp()
        self.url_user_invitee = reverse("user_invitee")
        self.url_reply_invite = reverse("user_invitee_reply")
        self.token = Token.objects.create(user=self.user_invitee)
        self.api_authentication()

    def tearDown(self):
        User.objects.all().delete()

    def test_success_get_invite_info(self):
        # Given: 사용자
        # When: 사용자가 자신이 초대받은 프로젝트의 정보를 조회할 때
        url = self.url_user_invitee
        response = self.client.get(url)

        expected_response = {
            "success": True,
            "result": [
                {
                    "project_id": self.project.id,
                    "inviter_email": self.user_inviter.email,
                    "created_at": self.time_check_v,
                }
            ],
        }

        # Then: 응답 코드는 200이고 해당 정보를 반환한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json(), expected_response)

    def test_success_reply_invite_accept(self):
        # Given: 사용자
        # When: 사용자가 초대를 수락할 때
        url = self.url_reply_invite
        response = self.client.post(
            url,
            {
                "project_id": self.project.id,
                "inviter_email": self.user_inviter.email,
                "accept": True,
            },
        )

        # Then: 응답 코드는 200이고. 초대가 수락된다.
        # 초대를 수락한 사용자는 프로젝트의 멤버가 된다.
        # 초대 내용은 삭제된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(self.project.projectmember_set.count(), 2)
        self.assertEqual(self.project.projectinvite_set.count(), 0)

    def test_success_reply_invite_deny(self):
        # Given: 사용자
        # When: 사용자가 초대를 거절할 때
        url = self.url_reply_invite
        response = self.client.post(
            url,
            {
                "project_id": self.project.id,
                "inviter_email": self.user_inviter.email,
                "accept": False,
            },
        )

        # Then: 응답 코드는 200이고. 초대가 거절된다.
        # 초대 내용은 삭제된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(self.project.projectmember_set.count(), 1)
        self.assertEqual(self.project.projectinvite_set.count(), 0)

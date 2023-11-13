from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from domo_api.const import ReturnCode
from domo_api.models import User
from domo_api.s3.handler import ProfileImageUploader
from PIL import Image
from rest_framework.test import APIClient


class SocialSignUpTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.social_signup_url = reverse("social_sign_up")
        self.user_email = "test@test.io"
        self.user_data = {
            "name": "춘식이",
            "pre_access_token": "VALID_PRE_ACCESS_TOKEN",
            "github_link": "https://github.com/testuser",
            "short_description": "나는 춘식이",
        }
        self.provider = "naver"
        image = Image.new("RGB", (100, 100))
        self.tmp_file = BytesIO()
        image.save(self.tmp_file, format="JPEG")
        self.tmp_file.seek(0)

    @patch("domo_api.tasks.update_github_history.delay")
    @patch.object(ProfileImageUploader, "upload_image")
    def test_social_sign_up_success(self, mock_upload_image, mock_github_delay):
        # Given: 유효한 사용자 정보와 함께 프로필 이미지가 주어졌을 때,
        mock_upload_image.return_value = (
            ReturnCode.SUCCESS,
            "https://domo-s3.s3.ap-northeast-2.amazonaws.com/users/some-user%40some-domain.some-TLD/"
            "profile/image/profile-image.jpeg",
        )

        User.objects.create(
            email=self.user_email,
            name="NOT REGISTERED",
            created_at=datetime.now(tz=timezone.utc),
            provider=self.provider,
            pre_access_token=self.user_data["pre_access_token"],
        )

        payload = self.user_data

        payload["profile_image"] = SimpleUploadedFile(
            "profile.jpg", self.tmp_file.read(), content_type="image/jpeg"
        )

        # When: 회원가입 API를 호출하면,
        response = self.client.post(self.social_signup_url, payload, format="multipart")

        # Then: 회원가입이 성공하고, 성공 메시지가 반환된다.
        user = User.objects.get(pre_access_token=self.user_data["pre_access_token"])
        mock_github_delay.assert_called_once_with(user.id, user.github_link)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["success"])

    @patch.object(ProfileImageUploader, "upload_image")
    def test_social_sign_up_with_profile_image_upload_failure(self, mock_upload_image):
        # Given: 이미지 업로드가 실패하는 상황에서,
        mock_upload_image.return_value = ReturnCode.FAIL, None

        User.objects.create(
            email=self.user_email,
            name="NOT REGISTERED",
            created_at=datetime.now(tz=timezone.utc),
            provider=self.provider,
            pre_access_token=self.user_data["pre_access_token"],
        )

        payload = self.user_data

        payload["profile_image"] = SimpleUploadedFile(
            "profile.jpg", self.tmp_file.read(), content_type="image/jpeg"
        )

        # When: 회원가입 API를 호출하면,
        response = self.client.post(self.social_signup_url, payload, format="multipart")

        # Then: 이미지 업로드 실패로 인해 회원가입이 실패한다.
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Error uploading profile image.")

    #######

    def test_social_sign_up_user_already_exists(self):
        # Given: 이미 OAuth를 통해 가입된 사용자가 재시도할 때,
        User.objects.create(
            email=self.user_email,
            name="REGISTERED",
            created_at=datetime.now(tz=timezone.utc),
            provider=self.provider,
            pre_access_token=self.user_data["pre_access_token"],
        )

        payload = self.user_data

        # When: 회원가입 API를 호출하면,
        response = self.client.post(self.social_signup_url, payload, format="json")

        # Then: 이미 회원이라는 메시지가 반환된다.
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "User is already registered.")

    def test_social_sign_up_without_pre_signup(self):
        # Given: pre-signup 이전 회원가입 시도할 시
        payload = self.user_data

        # When: 회원가입 API를 호출하면,
        response = self.client.post(self.social_signup_url, payload, format="json")

        # Then: 이메일 인증을 하지 않았다는 메세지를 출력한다.
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "User not pre-registered.")

    def test_social_sign_up_invalid_payload(self):
        # Given: 유효하지 않은 사용자 정보가 주어졌을 때,
        payload = {
            "pre_access_token": self.user_data["pre_access_token"],
            # 이름이 누락됨
        }

        # When: 회원가입 API를 호출하면,
        response = self.client.post(self.social_signup_url, payload, format="json")

        # Then: 유효하지 않은 요청으로 인해 회원가입이 실패한다.
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid request.")

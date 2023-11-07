# from datetime import datetime, timezone
# from io import BytesIO
# from unittest.mock import patch
#
# from django.core.files.uploadedfile import SimpleUploadedFile
# from django.test import TestCase
# from django.urls import reverse
# from domo_api.const import ReturnCode
# from domo_api.models import User
# from domo_api.s3.image import Uploader
# from PIL import Image
# from rest_framework.test import APIClient
#
#
# class SignUpTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.signup_url = reverse("sign_up")
#         self.user_data = {
#             "email": "test@example.com",
#             "password": "VAL1DP@sSW0Rd",
#             "name": "춘식이",
#             "github_link": "https://github.com/testuser",
#             "short_description": "나는 춘식이",
#         }
#         image = Image.new("RGB", (100, 100))
#         self.tmp_file = BytesIO()
#         image.save(self.tmp_file, format="JPEG")
#         self.tmp_file.seek(0)
#
#     def test_sign_up_success(self):
#         # Given: 유효한 사용자 정보가 주어졌을 때,
#         User.objects.create(
#             email=self.user_data["email"],
#             name="NOT REGISTERED",
#             created_at=datetime.now(tz=timezone.utc),
#             provider="our",
#         )
#
#         payload = self.user_data
#
#         # When: 회원가입 API를 호출하면,
#         response = self.client.post(self.signup_url, payload, format="json")
#
#         # Then: 회원가입이 성공하고, 성공 메시지가 반환된다.
#         self.assertEqual(response.status_code, 201)
#         self.assertTrue(response.json()["success"])
#
#     def test_sign_up_email_already_exists(self):
#         # Given: 이미 존재하는 이메일로 회원가입을 시도할 때,
#         User.objects.create_user(**self.user_data)
#         payload = self.user_data
#
#         # When: 회원가입 API를 호출하면,
#         response = self.client.post(self.signup_url, payload, format="json")
#
#         # Then: 이미 존재하는 이메일로는 회원가입이 불가하다는 메시지가 반환된다.
#         self.assertEqual(response.status_code, 400)
#         self.assertFalse(response.json()["success"])
#         self.assertEqual(
#             response.json()["reason"], "User with this email already exists."
#         )
#
#     def test_sign_up_without_email_verify(self):
#         # Given: 이메일 인증 전 회원가입 시도할 시
#         payload = self.user_data
#
#         # When: 회원가입 API를 호출하면,
#         response = self.client.post(self.signup_url, payload, format="json")
#
#         # Then: 이메일 인증을 하지 않았다는 메세지를 출력한다.
#         self.assertEqual(response.status_code, 400)
#         self.assertFalse(response.json()["success"])
#         self.assertEqual(response.json()["reason"], "User didn't verify email yet.")
#
#     def test_sign_up_invalid_payload(self):
#         # Given: 유효하지 않은 사용자 정보가 주어졌을 때,
#         payload = {
#             "email": "test@example.com",
#             # 비밀번호가 누락됨
#             "name": "Test User",
#         }
#
#         # When: 회원가입 API를 호출하면,
#         response = self.client.post(self.signup_url, payload, format="json")
#
#         # Then: 유효하지 않은 요청으로 인해 회원가입이 실패한다.
#         self.assertEqual(response.status_code, 400)
#         self.assertFalse(response.json()["success"])
#         self.assertEqual(response.json()["reason"], "Invalid request.")
#
#     def test_sign_up_invalid_email_format(self):
#         # Given: 잘못된 이메일 형식으로 회원가입을 시도할 때,
#         invalid_email_data = self.user_data.copy()
#         invalid_email_data["email"] = "testexample.com"
#
#         # When: 회원가입 API를 호출하면,
#         response = self.client.post(self.signup_url, invalid_email_data, format="json")
#
#         # Then: 잘못된 이메일 형식으로 인해 회원가입이 실패한다.
#         self.assertEqual(response.status_code, 400)
#         self.assertFalse(response.json()["success"])
#         self.assertEqual(response.json()["reason"], "Invalid request.")
#
#     # @patch("domo_api.models.User.objects.update")
#     # def test_sign_up_server_error(self, mock_create_user):
#     #     # Given: 서버 내부 오류가 발생할 때(예: DB 연결 오류),
#     #     # mock_create_user 메서드가 Exception을 발생시키도록 설정
#     #     # email verify 완료된 상황
#     #
#     #     mock_create_user.side_effect = Exception("DB Error")
#     #
#     #     User.objects.create(
#     #         email=self.user_data["email"],
#     #         name="NOT REGISTERED",
#     #         created_at=datetime.now(tz=timezone.utc),
#     #     )
#     #
#     #     # When: 회원가입 API를 호출하면,
#     #     response = self.client.post(self.signup_url, self.user_data, format="json")
#     #
#     #     # Then: 서버 내부 오류로 인해 회원가입이 실패한다.
#     #     self.assertEqual(response.status_code, 500)
#     #     self.assertFalse(response.json()["success"])
#     #     self.assertEqual(response.json()["reason"], "Error creating user.")
#
#     @patch.object(Uploader, "upload_image")
#     def test_sign_up_with_valid_profile_image(self, mock_upload_image):
#         # Given: 유효한 사용자 정보와 함께 프로필 이미지가 주어졌을 때,
#         # email verify 완료된 상황
#         mock_upload_image.return_value = ReturnCode.SUCCESS, "SOME_URL"
#
#         User.objects.create(
#             email=self.user_data["email"],
#             name="NOT REGISTERED",
#             created_at=datetime.now(tz=timezone.utc),
#             provider="our",
#         )
#
#         payload = self.user_data
#
#         payload["profile_image"] = SimpleUploadedFile(
#             "profile.jpg", self.tmp_file.read(), content_type="image/jpeg"
#         )
#
#         # When: 회원가입 API를 호출하면,
#         response = self.client.post(self.signup_url, payload, format="multipart")
#
#         # Then: 회원가입이 성공하고, 성공 메시지가 반환된다.
#         self.assertEqual(response.status_code, 201)
#         self.assertTrue(response.json()["success"])
#
#     @patch.object(Uploader, "upload_image")
#     def test_sign_up_with_profile_image_upload_failure(self, mock_upload_image):
#         # Given: 이미지 업로드가 실패하는 상황에서,
#         # email verify 완료된 상황
#         mock_upload_image.return_value = ReturnCode.FAIL, None
#
#         User.objects.create(
#             email=self.user_data["email"],
#             name="NOT REGISTERED",
#             created_at=datetime.now(tz=timezone.utc),
#             provider="our",
#         )
#
#         payload = self.user_data
#
#         payload["profile_image"] = SimpleUploadedFile(
#             "profile.jpg", self.tmp_file.read(), content_type="image/jpeg"
#         )
#
#         # When: 회원가입 API를 호출하면,
#         response = self.client.post(self.signup_url, payload, format="multipart")
#
#         # Then: 이미지 업로드 실패로 인해 회원가입이 실패한다.
#         self.assertEqual(response.status_code, 500)
#         self.assertFalse(response.json()["success"])
#         self.assertEqual(response.json()["reason"], "Error uploading profile image.")

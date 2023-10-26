from django.test import TestCase
from django.urls import reverse
from domo_api.models import User


class SignInTest(TestCase):
    def setUp(self):
        # Given: 유효한 계정을 생성
        self.sign_in_url = reverse("sign_in")
        self.user_data = {
            "email": "test@example.com",
            "password": "VAL1DP@sSW0Rd",
            "name": "춘식이",
        }
        User.objects.create_user(**self.user_data)

    def test_sign_in_successful(self):
        # When: 유효한 계정 정보로 로그인 요청을 보내면,
        response = self.client.post(self.sign_in_url, self.user_data, format="json")

        # Then: 로그인이 성공한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertTrue("token" in response.json())

    def test_sign_in_wrong_password(self):
        # Given: 유효하지 않은 비밀번호로,
        invalid_data = self.user_data.copy()
        invalid_data["password"] = "wrongpassword"

        # When: 로그인 요청을 보내면,
        response = self.client.post(self.sign_in_url, invalid_data, format="json")

        # Then: 로그인이 실패한다.
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Email or Password is incorrect.")

    def test_sign_in_wrong_email(self):
        # Given: 유효하지 않은 이메일로,
        invalid_data = self.user_data.copy()
        invalid_data["email"] = "wrong@example.com"

        # When: 로그인 요청을 보내면,
        response = self.client.post(self.sign_in_url, invalid_data, format="json")

        # Then: 로그인이 실패한다.
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Email or Password is incorrect.")

    def test_sign_in_bad_request(self):
        # Given: 비밀번호 필드가 누락된 경우에서,
        bad_data = {"email": "test@example.com"}

        # When: 로그인 요청을 보내면,
        response = self.client.post(self.sign_in_url, bad_data, format="json")

        # Then: 잘못된 요청으로 로그인이 실패한다.
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["reason"], "Invalid request.")

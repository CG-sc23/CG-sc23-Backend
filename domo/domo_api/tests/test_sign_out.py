from django.urls import reverse
from domo_api.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class SignOutTest(APITestCase):
    def setUp(self):
        self.sign_out_url = reverse("sign_out")
        self.user = User.objects.create_user(
            email="test@example.com",
            password="VAL1DP@sSW0Rd",
            name="춘식이",
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_sign_out_successful(self):
        # Given: 유효한 토큰을 사용하여,
        # When: 로그아웃 요청을 보내면,
        response = self.client.get(self.sign_out_url)

        # Then: 로그아웃이 성공한다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(
            Token.objects.filter(key=self.token.key).exists()
        )  # 토큰이 삭제되었는지 확인

    def test_sign_out_unauthenticated(self):
        # Given: 토큰을 사용하지 않거나 유효하지 않은 토큰으로,
        self.client.force_authenticate(user=None)  # 인증 제거

        # When: 로그아웃 요청을 보내면,
        response = self.client.get(self.sign_out_url)

        # Then: 로그아웃이 실패한다.
        self.assertEqual(response.status_code, 401)

import os
from unittest import TestCase

from ads.models import Ad
from django.urls import reverse
from rest_framework.test import APIClient


class GoogleCallBackTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_google_cb = reverse("ads_google_cb")
        self.google_script_id = os.getenv("GOOGLE_SCRIPT_ID")
        self.google_sent_data = {
            "formId": "SOME_FORM_ID",
            "formTitle": "SOME_FORM_TITLE",
            "requesterEmail": "some_requester@domain.com",
            "results": [
                {
                    "id": 1,
                    "response": "some_company@domain.com",
                    "title": "회사의 이메일을 입력해주세요.",
                    "type": "TEXT",
                },
                {
                    "id": 2,
                    "response": "SOME_COMPANY_NAME",
                    "title": "회사의 이름을 입력해주세요.",
                    "type": "TEXT",
                },
                {
                    "id": 3,
                    "response": "SOME_NAME",
                    "title": "담당자의 성함을 입력해주세요.",
                    "type": "TEXT",
                },
                {
                    "id": 4,
                    "response": "SOME_PURPOSE",
                    "title": "광고의 목적은 무엇인가요?",
                    "type": "TEXT",
                },
                {
                    "id": 5,
                    "response": "SOME_GOOGLE_DRIVE_LINK_POSTFIX",
                    "title": "광고로 게시할 사진을 올려주세요. (가로:세로 = 2:1)",
                    "type": "FILE_UPLOAD",
                },
            ],
        }

    def tearDown(self):
        Ad.objects.all().delete()

    def test_google_cb_success(self):
        # When: 구글 폼에서 요청이 오면
        response = self.client.post(
            self.url_google_cb,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; Google-Apps-Script; beanserver; +https://script.google.com; id: "
                f"{os.getenv('GOOGLE_SCRIPT_ID')}",
            },
            data=self.google_sent_data,
            format="json",
        )

        # Then: 응답 코드는 200이고, DB에 광고 요청 데이터가 추가된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertTrue(Ad.objects.all().count() == 1)

    def test_google_cb_but_requester_is_not_google(self):
        # When: 구글 폼이 아닌 곳에서 요청이 오면
        with self.assertRaises(PermissionError):
            response = self.client.post(
                self.url_google_cb,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; Google-Apps-Script; beanserver; +https://script.google.com; id: "
                    f"SOME_INVALID_SCRIPT_ID",
                },
                data=self.google_sent_data,
                format="json",
            )
            # Then: PermissionError 예외가 발생하고, 응답 코드는 403이다.
            self.assertEqual(response.status_code, 403)

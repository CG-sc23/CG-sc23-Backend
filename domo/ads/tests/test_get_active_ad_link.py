from datetime import datetime, timezone
from unittest import TestCase

from ads.models import Ad
from django.urls import reverse
from rest_framework.test import APIClient


class GetActiveAdLinkTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_get_ad_link = reverse("get_active_ad_link")
        self.idx = Ad.objects.create(
            requester_name="RR",
            requester_email="RR",
            company_name="RR",
            company_email="RR",
            purpose="RR",
            file_link="RR",
            initial_exposure_count=0,
            created_at=datetime.now(tz=timezone.utc),
            is_active=False,
        )
        self.ad_info = {
            "requester_name": "SOME_NAME",
            "requester_email": "SOME_EMAIL@domain.com",
            "company_name": "SOME_NAME",
            "company_email": "SOME_EMAIL@domain.com",
            "purpose": "SOME_PURPOSE",
            "file_link": "GOOGLE_DRIVE_LINK_POSTFIX",
            "initial_exposure_count": 10,
            "remaining_exposure_count": 10,
            "is_active": True,
            "created_at": datetime.now(tz=timezone.utc),
        }

    def tearDown(self):
        Ad.objects.all().delete()

    def test_get_ad_success(self):
        # Given: 광고가 존재할 때
        Ad.objects.create(**self.ad_info)
        # When: FrontEnd에서 요청이 오면
        response = self.client.get(
            self.url_get_ad_link,
        )

        # Then: 응답 코드는 200이고, 광고 자료 데이터가 반환된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(response.json()["file_link"] == "")

    def test_get_ad_but_no_active_ads(self):
        # Given: 광고가 존재하지 않을 때
        # When: FrontEnd에서 요청이 오면
        response = self.client.get(
            self.url_get_ad_link,
        )

        # Then: 응답 코드는 200이고, 빈 문자열이 반환된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertTrue(response.json()["file_link"] == "")

    def test_get_ad_but_idx_error(self):
        # Given: 어떠한 문제로 인덱스 행이 광고를 가리키지 않을 때
        self.idx.initial_exposure_count = 100
        self.idx.save()
        Ad.objects.create(**self.ad_info)

        # When: FrontEnd에서 요청이 오면
        response = self.client.get(
            self.url_get_ad_link,
        )

        # Then: 응답 코드는 200이고, 적절한 광고가 반환된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(response.json()["file_link"] == "")

    def test_ad_deactivate(self):
        # Given: 노출 횟수가 1회 남은 광고가 존재할 때
        ad_remaining_exposure_count_one = self.ad_info.copy()
        ad_remaining_exposure_count_one["remaining_exposure_count"] = 1
        ad_obj = Ad.objects.create(**ad_remaining_exposure_count_one)

        # When: FrontEnd에서 요청이 오면
        response = self.client.get(
            self.url_get_ad_link,
        )

        # Then: 응답 코드는 200이고, 광고 자료 데이터가 반환된다.
        # 그리고 광고의 남은 노출 횟수가 0이 되면서, 광고가 비활성화된다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(response.json()["file_link"] == "")
        ad_obj.refresh_from_db()
        self.assertFalse(ad_obj.is_active)

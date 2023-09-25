from django.test import TestCase
from rest_framework.test import APIClient


class HealthCheckTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_success(self):
        response = self.client.get(
            "/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

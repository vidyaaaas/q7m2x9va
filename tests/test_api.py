import unittest
from fastapi.testclient import TestClient
from backend.main import app

class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(app)

    def test_health(self):
        self.assertEqual(self.client.get('/api/health').json()['status'],'ok')

    def test_invalid_date_and_time(self):
        self.assertEqual(self.client.get('/api/day?date=2026-02-01').status_code,422)
        self.assertEqual(self.client.get('/api/day?cutoff=25:00').status_code,422)

    def test_complete_day_and_export(self):
        day=self.client.get('/api/day?date=2026-01-31').json()
        self.assertEqual(day['deliveryDate'],'2026-02-01')
        self.assertEqual(day['forecastHours'],24)
        csv=self.client.get('/api/export?date=2026-01-31')
        self.assertEqual(len(csv.text.strip().splitlines()),25)

    def test_provenance(self):
        manifest=self.client.get('/api/provenance').json()
        self.assertEqual(len(manifest['files']['forecasts']['sha256']),64)

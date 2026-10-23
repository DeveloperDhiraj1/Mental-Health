import os
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import app


class ApiTests(unittest.TestCase):
    def test_health_and_model_info(self):
        with TestClient(app) as client:
            health = client.get("/health")
            info = client.get("/api/v1/model/info")
        self.assertEqual(health.status_code, 200)
        self.assertFalse(health.json()["model_available"])
        self.assertEqual(info.status_code, 200)
        self.assertFalse(info.json()["available"])

    def test_validation_and_missing_model(self):
        with TestClient(app) as client:
            self.assertEqual(client.post("/api/v1/predictions", json={"text": ""}).status_code, 422)
            self.assertEqual(client.post("/api/v1/predictions", json={"text": "hello"}).status_code, 503)
            self.assertEqual(client.post("/api/v1/predictions", json={"text": "x" * 5001}).status_code, 422)

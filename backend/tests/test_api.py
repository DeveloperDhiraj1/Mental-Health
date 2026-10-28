import os
import sys
import unittest
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

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
            self.assertEqual(client.post("/api/v1/predictions/batch", json={"texts": ["one"] * 4}).status_code, 422)
            self.assertEqual(client.post("/api/v1/predictions/batch", json={"texts": ["one"] * 5}).status_code, 503)

    def test_image_upload_is_validated_and_explicitly_unsupported(self):
        image_stream = BytesIO()
        Image.new("RGB", (1, 1), "white").save(image_stream, format="PNG")
        image_stream.seek(0)
        with TestClient(app) as client:
            invalid = client.post("/api/v1/image-analysis", files={"files": ("note.txt", b"hello", "text/plain")})
            malformed = client.post("/api/v1/image-analysis", files={"files": ("fake.png", b"\x89PNG\r\n\x1a\nnot-an-image", "image/png")})
            valid_but_unsupported = client.post("/api/v1/image-analysis", files={"files": ("pixel.png", image_stream, "image/png")})
        self.assertEqual(invalid.status_code, 415)
        self.assertEqual(malformed.status_code, 415)
        self.assertEqual(valid_but_unsupported.status_code, 501)

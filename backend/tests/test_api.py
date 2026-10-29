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
            ready = client.get("/ready")
            info = client.get("/api/v1/model/info")
            docs = client.get("/docs")
            openapi = client.get("/openapi.json")
        self.assertEqual(health.status_code, 200)
        self.assertFalse(health.json()["model_available"])
        self.assertEqual(ready.status_code, 503)
        self.assertEqual(info.status_code, 200)
        self.assertFalse(info.json()["available"])
        self.assertEqual(docs.status_code, 200)
        self.assertEqual(openapi.status_code, 200)
        self.assertIn("/api/v1/image-analysis", openapi.json()["paths"])
        self.assertIn("X-Content-Type-Options", health.headers)

    def test_request_size_guard(self):
        with TestClient(app) as client:
            response = client.post("/api/v1/predictions", content=b"x", headers={"content-length": str(16 * 1024 * 1024 + 1)})
        self.assertEqual(response.status_code, 413)

    def test_cors_allows_configured_frontend_origin(self):
        with TestClient(app) as client:
            response = client.options("/health", headers={"Origin": "http://127.0.0.1:5500", "Access-Control-Request-Method": "GET"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://127.0.0.1:5500")

    def test_validation_and_missing_model(self):
        with TestClient(app) as client:
            self.assertEqual(client.post("/api/v1/predictions", json={"text": ""}).status_code, 422)
            self.assertEqual(client.post("/api/v1/predictions", json={"text": "hello"}).status_code, 503)
            self.assertEqual(client.post("/api/v1/predictions", json={"text": "x" * 5001}).status_code, 422)
            self.assertEqual(client.post("/api/v1/predictions/batch", json={"texts": ["one"] * 4}).status_code, 422)
            self.assertEqual(client.post("/api/v1/predictions/batch", json={"texts": ["one"] * 5}).status_code, 503)

    def test_image_upload_is_validated_and_explicitly_unsupported(self):
        with TestClient(app) as client:
            invalid = client.post("/api/v1/image-analysis", files={"files": ("note.txt", b"hello", "text/plain")})
            malformed = client.post("/api/v1/image-analysis", files={"files": ("fake.png", b"\x89PNG\r\n\x1a\nnot-an-image", "image/png")})
            valid_statuses = []
            for extension, mime, format_name in (("jpg", "image/jpeg", "JPEG"), ("png", "image/png", "PNG"), ("webp", "image/webp", "WEBP")):
                image_stream = BytesIO()
                Image.new("RGB", (1, 1), "white").save(image_stream, format=format_name)
                image_stream.seek(0)
                valid_statuses.append(client.post("/api/v1/image-analysis", files={"files": (f"pixel.{extension}", image_stream, mime)}).status_code)
            oversized = client.post("/api/v1/image-analysis", files={"files": ("large.jpg", b"\xff\xd8\xff" + b"0" * (5 * 1024 * 1024), "image/jpeg")})
            too_many = client.post("/api/v1/image-analysis", files=[("files", (f"{index}.png", b"\x89PNG\r\n\x1a\n", "image/png")) for index in range(11)])
        self.assertEqual(invalid.status_code, 415)
        self.assertEqual(malformed.status_code, 415)
        self.assertEqual(valid_statuses, [501, 501, 501])
        self.assertEqual(oversized.status_code, 413)
        self.assertEqual(too_many.status_code, 413)

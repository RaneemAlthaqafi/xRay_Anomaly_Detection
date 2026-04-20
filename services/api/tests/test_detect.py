"""Integration tests. Model-heavy tests are skipped unless weights exist."""
from __future__ import annotations

import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.config import settings
from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_image_bytes() -> bytes:
    """A blank RGB image — sufficient to exercise the pipeline end-to-end."""
    img = Image.new("RGB", (640, 640), color=(128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_classes_endpoint(client: TestClient) -> None:
    r = client.get("/api/classes")
    assert r.status_code == 200
    data = r.json()
    assert len(data["classes"]) == 5
    assert data["classes"][0]["name_ar"] == "مسدس"
    assert data["classes"][1]["name_ar"] == "سكين"


def test_unsupported_media_type(client: TestClient) -> None:
    r = client.post(
        "/api/detect",
        files={"image": ("x.txt", b"not an image", "text/plain")},
    )
    assert r.status_code == 415


@pytest.mark.skipif(
    not Path(settings.MODEL_PATH).exists(),
    reason=f"Weights not found at {settings.MODEL_PATH} — skipping model-dependent test.",
)
def test_detect_roundtrip(client: TestClient, sample_image_bytes: bytes) -> None:
    r = client.post(
        "/api/detect",
        files={"image": ("sample.jpg", sample_image_bytes, "image/jpeg")},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "detections" in data
    assert "annotated_image_b64" in data
    assert data["image_width"] == 640
    assert data["image_height"] == 640
    assert data["inference_ms"] > 0

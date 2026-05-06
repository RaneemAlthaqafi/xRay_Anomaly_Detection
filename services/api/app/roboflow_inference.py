"""Roboflow hosted model wrapper."""
from __future__ import annotations

import base64
import io
import time

import httpx
from PIL import Image

from .config import settings
from .schemas import CLASS_NAMES_AR_BY_EN, CLASS_SEVERITY_BY_EN


class RoboflowDetector:
    """Detector backed by a Roboflow Universe hosted model."""

    _instance: "RoboflowDetector | None" = None

    def __init__(self) -> None:
        if not settings.ROBOFLOW_API_KEY:
            raise ValueError("ROBOFLOW_API_KEY is required when INFERENCE_PROVIDER=roboflow")
        self.model_name = f"roboflow:{settings.ROBOFLOW_MODEL_ID}"
        self.names = {
            0: "scissors",
            1: "gun",
            2: "knife",
            3: "wrench",
            4: "pliers",
        }

    @classmethod
    def get(cls) -> "RoboflowDetector":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def predict(self, image_bytes: bytes) -> tuple[Image.Image, list[dict], float]:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        encoded = base64.b64encode(image_bytes).decode("ascii")
        url = f"{settings.ROBOFLOW_API_BASE.rstrip('/')}/{settings.ROBOFLOW_MODEL_ID}"

        t0 = time.perf_counter()
        response = httpx.post(
            url,
            params={
                "api_key": settings.ROBOFLOW_API_KEY,
                "confidence": int(settings.CONF_THRESHOLD * 100),
                "overlap": int(settings.IOU_THRESHOLD * 100),
                "format": "json",
            },
            content=encoded,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=45.0,
        )
        inference_ms = (time.perf_counter() - t0) * 1000.0
        response.raise_for_status()
        payload = response.json()

        detections: list[dict] = []
        for pred in payload.get("predictions", []):
            raw_name = str(pred.get("class", pred.get("class_name", ""))).strip()
            name_en = self._normalize_name(raw_name)
            class_id = self._class_id(name_en, pred.get("class_id"))
            confidence = float(pred.get("confidence", 0.0))
            x = float(pred.get("x", 0.0))
            y = float(pred.get("y", 0.0))
            width = float(pred.get("width", 0.0))
            height = float(pred.get("height", 0.0))

            detections.append({
                "class_id": class_id,
                "class_name_en": name_en,
                "class_name_ar": CLASS_NAMES_AR_BY_EN.get(name_en, f"فئة {class_id}"),
                "severity": CLASS_SEVERITY_BY_EN.get(name_en, "medium"),
                "confidence": confidence,
                "bbox": [
                    x - width / 2,
                    y - height / 2,
                    x + width / 2,
                    y + height / 2,
                ],
            })

        return image, detections, inference_ms

    @staticmethod
    def _normalize_name(name: str) -> str:
        value = name.lower().replace("-", " ").replace("_", " ").strip()
        numeric = {
            "0": "scissors",
            "1": "gun",
            "2": "knife",
            "3": "wrench",
            "4": "pliers",
        }
        if value in numeric:
            return numeric[value]
        aliases = {
            "guns": "gun",
            "knives": "knife",
            "plier": "pliers",
            "scissor": "scissors",
            "wrenches": "wrench",
        }
        return aliases.get(value, value)

    def _class_id(self, name_en: str, raw_class_id: object) -> int:
        for class_id, class_name in self.names.items():
            if class_name == name_en:
                return class_id
        try:
            return int(raw_class_id)
        except (TypeError, ValueError):
            return 999

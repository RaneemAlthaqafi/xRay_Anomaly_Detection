"""YOLO model wrapper — singleton loader + predict()."""
from __future__ import annotations

import io
import logging
import time
from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from .config import settings
from .schemas import CLASS_NAMES_AR, CLASS_NAMES_AR_BY_EN, CLASS_NAMES_EN, CLASS_SEVERITY, CLASS_SEVERITY_BY_EN

logger = logging.getLogger(__name__)


class Detector:
    """Lazy-loaded YOLO detector. One instance per process."""

    _instance: "Detector | None" = None

    def __init__(self, model_path: Path):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model weights not found at {model_path}. "
                "Copy best.onnx to data/weights/ or set MODEL_PATH to the ONNX file."
            )
        logger.info("Loading YOLO model from %s", model_path)
        # Explicit task='detect' so ONNX weights load without metadata lookup.
        self.model = YOLO(str(model_path), task="detect")
        self.model_name = model_path.name
        self.names = self._model_names()

    def _model_names(self) -> dict[int, str]:
        names = getattr(self.model, "names", None)
        if isinstance(names, dict):
            return {int(k): str(v) for k, v in names.items()}
        if isinstance(names, list):
            return {i: str(v) for i, v in enumerate(names)}
        return {i: name for i, name in enumerate(CLASS_NAMES_EN)}

    @classmethod
    def get(cls) -> "Detector":
        if cls._instance is None:
            cls._instance = cls(settings.effective_model_path)
        return cls._instance

    def predict(self, image_bytes: bytes) -> tuple[Image.Image, list[dict], float]:
        """Run inference on raw image bytes.

        Returns (PIL image, list of detections dicts, inference_ms).
        Each detection dict: {class_id, class_name_en, class_name_ar, severity, confidence, bbox}.
        """
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        t0 = time.perf_counter()
        results = self.model.predict(
            source=image,
            imgsz=settings.IMG_SIZE,
            conf=settings.CONF_THRESHOLD,
            iou=settings.IOU_THRESHOLD,
            verbose=False,
        )
        inference_ms = (time.perf_counter() - t0) * 1000.0

        detections: list[dict] = []
        if results:
            boxes = results[0].boxes
            if boxes is not None and len(boxes) > 0:
                xyxy = boxes.xyxy.cpu().numpy()
                confs = boxes.conf.cpu().numpy()
                classes = boxes.cls.cpu().numpy().astype(int)
                for (x1, y1, x2, y2), conf, cls in zip(xyxy, confs, classes):
                    cls = int(cls)
                    name_en = self.names.get(
                        cls,
                        CLASS_NAMES_EN[cls] if cls < len(CLASS_NAMES_EN) else f"class_{cls}",
                    )
                    detections.append({
                        "class_id": cls,
                        "class_name_en": name_en,
                        "class_name_ar": CLASS_NAMES_AR_BY_EN.get(
                            name_en,
                            CLASS_NAMES_AR[cls] if cls < len(CLASS_NAMES_AR) else f"فئة {cls}",
                        ),
                        "severity": CLASS_SEVERITY_BY_EN.get(
                            name_en,
                            CLASS_SEVERITY[cls] if cls < len(CLASS_SEVERITY) else "medium",
                        ),
                        "confidence": float(conf),
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    })

        return image, detections, inference_ms

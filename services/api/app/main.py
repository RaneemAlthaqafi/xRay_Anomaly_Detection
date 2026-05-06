"""FastAPI application entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .inference import Detector
from .roboflow_inference import RoboflowDetector
from .routes.detect import router as detect_router
from .schemas import CLASS_NAMES_AR, CLASS_NAMES_EN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [api] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm the model at startup so the first request isn't slow.
    try:
        if settings.INFERENCE_PROVIDER.lower() == "roboflow":
            RoboflowDetector.get()
        else:
            Detector.get()
        logger.info("Model preloaded")
    except (FileNotFoundError, ValueError) as e:
        logger.warning("Model not loaded at startup: %s", e)
        logger.warning("First /api/detect call will fail until weights are present.")
    yield


app = FastAPI(
    title="xRay Anomaly Detection API",
    description="YOLOv11-based detection of prohibited items in baggage X-ray scans (Saudi Ports).",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(detect_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/model-status")
def model_status() -> dict:
    model_path = settings.effective_model_path
    if settings.INFERENCE_PROVIDER.lower() == "roboflow":
        detector = RoboflowDetector.get() if settings.ROBOFLOW_API_KEY else None
    else:
        detector = Detector.get() if model_path.exists() else None
    return {
        "provider": settings.INFERENCE_PROVIDER,
        "model_path": str(model_path),
        "model_name": detector.model_name if detector else model_path.name,
        "connected": bool(settings.ROBOFLOW_API_KEY) if settings.INFERENCE_PROVIDER.lower() == "roboflow" else model_path.exists(),
        "confidence_threshold": settings.CONF_THRESHOLD,
        "iou_threshold": settings.IOU_THRESHOLD,
        "image_size": settings.IMG_SIZE,
        "class_names": detector.names if detector else dict(enumerate(CLASS_NAMES_EN)),
    }


@app.get("/api/classes")
def classes() -> dict:
    """Class metadata — used by the frontend for the legend/filter."""
    return {
        "classes": [
            {"id": i, "name_en": en, "name_ar": ar}
            for i, (en, ar) in enumerate(zip(CLASS_NAMES_EN, CLASS_NAMES_AR))
        ]
    }

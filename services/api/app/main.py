"""FastAPI application entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .inference import Detector
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
        Detector.get()
        logger.info("Model preloaded")
    except FileNotFoundError as e:
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


@app.get("/api/classes")
def classes() -> dict:
    """Class metadata — used by the frontend for the legend/filter."""
    return {
        "classes": [
            {"id": i, "name_en": en, "name_ar": ar}
            for i, (en, ar) in enumerate(zip(CLASS_NAMES_EN, CLASS_NAMES_AR))
        ]
    }

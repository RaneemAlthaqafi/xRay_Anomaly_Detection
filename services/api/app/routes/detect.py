"""POST /api/detect — single-image inference endpoint."""
from __future__ import annotations

import base64
import io

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from ..annotate_ar import annotate
from ..config import settings
from ..inference import Detector
from ..schemas import Detection, DetectResponse

router = APIRouter(prefix="/api", tags=["detection"])

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}


@router.post("/detect", response_model=DetectResponse)
async def detect(image: UploadFile = File(..., description="X-ray image (JPEG/PNG/WebP, ≤10 MB)")) -> DetectResponse:
    if image.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type: {image.content_type}. Allowed: {sorted(ALLOWED_MIME)}",
        )

    raw = await image.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image exceeds {settings.MAX_UPLOAD_MB} MB",
        )

    detector = Detector.get()
    try:
        pil_img, dets, infer_ms = detector.predict(raw)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {e}",
        ) from e

    annotated = annotate(pil_img, dets, font_path=settings.FONT_PATH)

    buf = io.BytesIO()
    annotated.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    return DetectResponse(
        detections=[Detection(**d) for d in dets],
        annotated_image_b64=b64,
        image_width=pil_img.width,
        image_height=pil_img.height,
        inference_ms=round(infer_ms, 2),
        model_name=detector.model_name,
    )

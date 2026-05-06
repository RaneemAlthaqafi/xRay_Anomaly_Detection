"""POST /api/detect — single-image inference endpoint."""
from __future__ import annotations

import base64
import io

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from ..annotate_ar import annotate
from ..config import settings
from ..inference import Detector
from ..roboflow_inference import RoboflowDetector
from ..schemas import Detection, DetectResponse

router = APIRouter(prefix="/api", tags=["detection"])

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}


def decision_summary(detections: list[dict]) -> dict:
    if not detections:
        return {
            "risk_level": "clear",
            "risk_score": 0,
            "inspection_priority": "normal",
            "recommended_action_en": "Review the full image, then clear the bag if nothing else looks suspicious.",
            "recommended_action_ar": "راجع الصورة كاملة، ثم اسمح بمرور الحقيبة إذا لم يظهر شيء مشتبه.",
        }

    severity_weight = {"high": 100, "medium": 72, "low": 45}
    top = max(
        detections,
        key=lambda d: severity_weight.get(d["severity"], 60) * d["confidence"],
    )
    risk_score = round(severity_weight.get(top["severity"], 60) * top["confidence"])

    if top["severity"] == "high" or risk_score >= 70:
        return {
            "risk_level": "high",
            "risk_score": min(100, risk_score),
            "inspection_priority": "urgent",
            "recommended_action_en": "Hold the bag and send it to manual inspection immediately.",
            "recommended_action_ar": "أوقف الحقيبة وحوّلها للتفتيش اليدوي فورا.",
        }

    return {
        "risk_level": "medium",
        "risk_score": min(100, risk_score),
        "inspection_priority": "review",
        "recommended_action_en": "Review the highlighted area before clearing the bag.",
        "recommended_action_ar": "راجع المنطقة المحددة قبل السماح بمرور الحقيبة.",
    }


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

    detector = RoboflowDetector.get() if settings.INFERENCE_PROVIDER.lower() == "roboflow" else Detector.get()
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
        **decision_summary(dets),
    )

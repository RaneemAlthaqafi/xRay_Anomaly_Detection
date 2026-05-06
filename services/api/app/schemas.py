from pydantic import BaseModel, Field


CLASS_NAMES_EN: list[str] = ["gun", "knife", "pliers", "scissors", "wrench"]
CLASS_NAMES_AR: list[str] = ["مسدس", "سكين", "كماشة", "مقص", "مفتاح ربط"]
CLASS_NAMES_AR_BY_EN: dict[str, str] = dict(zip(CLASS_NAMES_EN, CLASS_NAMES_AR))

# Risk tier shown in the UI. Gun/knife = high; the rest = medium.
CLASS_SEVERITY: list[str] = ["high", "high", "medium", "medium", "medium"]
CLASS_SEVERITY_BY_EN: dict[str, str] = dict(zip(CLASS_NAMES_EN, CLASS_SEVERITY))


class Detection(BaseModel):
    class_id: int = Field(..., ge=0)
    class_name_en: str
    class_name_ar: str
    severity: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: list[float] = Field(..., min_length=4, max_length=4, description="[x1, y1, x2, y2] in pixels")


class DetectResponse(BaseModel):
    detections: list[Detection]
    annotated_image_b64: str = Field(..., description="PNG, base64-encoded")
    image_width: int
    image_height: int
    inference_ms: float
    model_name: str
    risk_level: str
    risk_score: int = Field(..., ge=0, le=100)
    inspection_priority: str
    recommended_action_en: str
    recommended_action_ar: str

"""Image annotation for detector outputs."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SEVERITY_COLORS: dict[str, tuple[int, int, int]] = {
    "high": (220, 38, 38),
    "medium": (234, 179, 8),
    "low": (34, 197, 94),
}


def annotate(
    image: Image.Image,
    detections: list[dict],
    font_path: Path,
    font_size: int = 22,
    box_width: int = 3,
) -> Image.Image:
    """Draw bounding boxes and English labels on a copy of image."""
    img = image.convert("RGB").copy()
    draw = ImageDraw.Draw(img, "RGBA")

    try:
        font = ImageFont.truetype(str(font_path), font_size)
    except OSError:
        font = ImageFont.load_default()

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        conf = det["confidence"]
        severity = det.get("severity", "medium")
        color = SEVERITY_COLORS.get(severity, SEVERITY_COLORS["medium"])

        draw.rectangle([x1, y1, x2, y2], outline=color, width=box_width)

        # Use the provider-normalized class name. Class-id order differs between
        # the local ONNX and Roboflow, so never infer the display label here.
        name_en = str(det.get("class_name_en") or f"class_{det.get('class_id', '')}")
        label = f"{name_en}  {conf * 100:.0f}%"

        text_bbox = draw.textbbox((0, 0), label, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        pad_x, pad_y = 6, 4

        strip_x1 = max(0, x1)
        strip_x2 = min(img.width, strip_x1 + text_w + 2 * pad_x)
        strip_y1 = max(0, y1 - text_h - 2 * pad_y)
        strip_y2 = strip_y1 + text_h + 2 * pad_y

        draw.rectangle([strip_x1, strip_y1, strip_x2, strip_y2], fill=color + (230,))
        draw.text(
            (strip_x1 + pad_x, strip_y1 + pad_y - text_bbox[1]),
            label,
            font=font,
            fill=(255, 255, 255),
        )

    return img

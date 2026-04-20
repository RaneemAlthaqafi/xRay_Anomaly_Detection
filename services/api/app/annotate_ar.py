"""Arabic-aware image annotation for YOLO detections.

cv2.putText cannot shape Arabic: it draws disconnected glyphs left-to-right.
We render labels with PIL instead, after passing the string through
arabic-reshaper (contextual glyph shaping) and python-bidi (RTL logical→visual).
"""
from __future__ import annotations

from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

from .schemas import CLASS_NAMES_AR, CLASS_SEVERITY

# Box color per severity tier. Annotations are also tinted by class if you prefer.
SEVERITY_COLORS: dict[str, tuple[int, int, int]] = {
    "high": (220, 38, 38),     # red-600
    "medium": (234, 179, 8),   # yellow-500
    "low": (34, 197, 94),      # green-500
}


def _shape_ar(text: str) -> str:
    """Reshape Arabic for correct glyph connection + bidi order."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def annotate(
    image: Image.Image,
    detections: list[dict],
    font_path: Path,
    font_size: int = 22,
    box_width: int = 3,
) -> Image.Image:
    """Draw bounding boxes + shaped-Arabic labels on a copy of `image`."""
    img = image.convert("RGB").copy()
    draw = ImageDraw.Draw(img, "RGBA")

    try:
        font = ImageFont.truetype(str(font_path), font_size)
    except OSError:
        # Fallback; Arabic will not shape correctly but the service won't crash.
        font = ImageFont.load_default()

    for det in detections:
        cls = det["class_id"]
        x1, y1, x2, y2 = det["bbox"]
        conf = det["confidence"]
        severity = CLASS_SEVERITY[cls] if cls < len(CLASS_SEVERITY) else "medium"
        color = SEVERITY_COLORS[severity]

        # Box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=box_width)

        # Label text: "<ar> %"
        name_ar = CLASS_NAMES_AR[cls] if cls < len(CLASS_NAMES_AR) else f"#{cls}"
        label = f"{_shape_ar(name_ar)}  {conf * 100:.0f}%"

        # Measure label so we can draw a filled background strip for readability
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        pad_x, pad_y = 6, 4

        # Position the strip above the box if there's room, otherwise below the top edge.
        strip_y1 = max(0, y1 - text_h - 2 * pad_y)
        strip_y2 = strip_y1 + text_h + 2 * pad_y

        # Strip extends from the right edge of the box for RTL reading.
        strip_x2 = x2
        strip_x1 = strip_x2 - text_w - 2 * pad_x

        draw.rectangle([strip_x1, strip_y1, strip_x2, strip_y2], fill=color + (230,))
        draw.text(
            (strip_x1 + pad_x, strip_y1 + pad_y - bbox[1]),
            label,
            font=font,
            fill=(255, 255, 255),
        )

    return img

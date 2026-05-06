from __future__ import annotations

import argparse
import json
import random
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from ultralytics import YOLO


CLASS_NAMES_EN = ["gun", "knife", "pliers", "scissors", "wrench"]
CLASS_NAMES_AR = ["مسدس", "سكين", "كماشة", "مقص", "مفتاح ربط"]


@dataclass(frozen=True)
class Candidate:
    image_path: str
    label_path: str
    class_id: int
    bbox: tuple[float, float, float, float]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create high-confidence training examples for the web demo strip.")
    parser.add_argument("--zip", default="data/raw/xray-baggage.zip")
    parser.add_argument("--model", default="data/weights/best.onnx")
    parser.add_argument("--out", default="services/web/public/demo")
    parser.add_argument("--split", default="train")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.20)
    parser.add_argument("--iou-match", type=float, default=0.20)
    parser.add_argument("--min-confidence", type=float, default=0.45)
    parser.add_argument("--scan-per-class", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def yolo_to_xyxy(row: str, size: tuple[int, int]) -> tuple[int, tuple[float, float, float, float]]:
    cls_s, xc_s, yc_s, w_s, h_s = row.split()[:5]
    width, height = size
    xc, yc, w, h = map(float, [xc_s, yc_s, w_s, h_s])
    return int(cls_s), (
        (xc - w / 2) * width,
        (yc - h / 2) * height,
        (xc + w / 2) * width,
        (yc + h / 2) * height,
    )


def iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    denom = area_a + area_b - inter
    return inter / denom if denom else 0.0


def collect_candidates(zip_path: Path, split: str) -> dict[int, list[Candidate]]:
    by_class: dict[int, list[Candidate]] = {i: [] for i in range(len(CLASS_NAMES_EN))}
    with zipfile.ZipFile(zip_path) as z:
        label_names = sorted(n for n in z.namelist() if n.startswith(f"{split}/labels/") and n.endswith(".txt"))
        for label_name in label_names:
            rows = [r for r in z.read(label_name).decode("utf-8").splitlines() if r.strip()]
            if len(rows) != 1:
                continue

            image_name = label_name.replace(f"{split}/labels/", f"{split}/images/").replace(".txt", ".jpg")
            if image_name not in z.namelist():
                continue

            with z.open(image_name) as f:
                size = Image.open(f).size
            cls, bbox = yolo_to_xyxy(rows[0], size)
            if cls in by_class:
                by_class[cls].append(Candidate(image_name, label_name, cls, bbox))
    return by_class


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = collect_candidates(Path(args.zip), args.split)
    model = YOLO(args.model, task="detect")
    selected = []

    with zipfile.ZipFile(args.zip) as z, tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for cls, items in candidates.items():
            random.shuffle(items)
            best: dict | None = None
            for item in items[: args.scan_per_class]:
                extracted = tmp_dir / Path(item.image_path).name
                extracted.write_bytes(z.read(item.image_path))
                result = model.predict(
                    source=str(extracted),
                    imgsz=args.imgsz,
                    conf=args.conf,
                    verbose=False,
                )[0]
                if result.boxes is None:
                    continue

                for box in result.boxes:
                    pred_cls = int(box.cls.item())
                    pred_conf = float(box.conf.item())
                    pred_bbox = tuple(float(v) for v in box.xyxy[0].tolist())
                    overlap = iou(item.bbox, pred_bbox)
                    if pred_cls != cls or pred_conf < args.min_confidence or overlap < args.iou_match:
                        continue

                    if best is None or pred_conf > best["confidence"]:
                        best = {
                            "source": item.image_path,
                            "class_id": cls,
                            "class_name_en": CLASS_NAMES_EN[cls],
                            "class_name_ar": CLASS_NAMES_AR[cls],
                            "confidence": round(pred_conf, 4),
                            "iou": round(overlap, 4),
                            "filename": f"{cls}-{CLASS_NAMES_EN[cls]}.jpg",
                        }
                if best and best["confidence"] >= 0.75:
                    break

            if best is None:
                raise SystemExit(f"No reliable demo image found for class {cls} ({CLASS_NAMES_EN[cls]}).")

            (out_dir / best["filename"]).write_bytes(z.read(best["source"]))
            selected.append(best)
            print(best)

    (out_dir / "manifest.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()

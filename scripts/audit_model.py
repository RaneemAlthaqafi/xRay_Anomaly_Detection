from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit a YOLO baggage model on a folder of sample images.")
    parser.add_argument("--model", default="data/weights/best.onnx", help="Path to .onnx or .pt weights.")
    parser.add_argument("--images", default="samples", help="Folder containing JPG/PNG/WebP images.")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--thresholds", default="0.10,0.15,0.20,0.25,0.35,0.50")
    parser.add_argument("--out", default="runs/audit/current_model_thresholds.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image_dir = Path(args.images)
    files = sorted(
        p for p in image_dir.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )
    if not files:
        raise SystemExit(f"No images found in {image_dir}")

    thresholds = [float(v.strip()) for v in args.thresholds.split(",") if v.strip()]
    model = YOLO(args.model, task="detect")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for conf in thresholds:
        images_with_detection = 0
        total_boxes = 0
        avg_conf_sum = 0.0
        for image in files:
            result = model.predict(
                source=str(image),
                imgsz=args.imgsz,
                conf=conf,
                iou=args.iou,
                verbose=False,
            )[0]
            boxes = result.boxes
            count = 0 if boxes is None else len(boxes)
            total_boxes += count
            images_with_detection += int(count > 0)
            if count:
                avg_conf_sum += float(boxes.conf.mean().item())

        rows.append({
            "confidence_threshold": conf,
            "images": len(files),
            "images_with_detection": images_with_detection,
            "total_boxes": total_boxes,
            "avg_confidence_detected_images": round(avg_conf_sum / max(images_with_detection, 1), 4),
        })

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {out_path}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()

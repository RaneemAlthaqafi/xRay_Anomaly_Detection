from __future__ import annotations

import argparse
import json
import random
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw


CLASS_NAMES_EN = ["gun", "knife", "pliers", "scissors", "wrench"]
CLASS_NAMES_AR = ["مسدس", "سكين", "كماشة", "مقص", "مفتاح ربط"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a visual audit proving class-id to label mapping.")
    parser.add_argument("--zip", default="data/raw/xray-baggage.zip")
    parser.add_argument("--split", default="train", choices=["train", "valid", "test"])
    parser.add_argument("--per-class", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-dir", default="runs/audit/label_mapping")
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


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    by_class: dict[int, list[tuple[str, str, tuple[float, float, float, float]]]] = defaultdict(list)
    counts = Counter()

    with zipfile.ZipFile(args.zip) as z:
        names = set(z.namelist())
        label_names = sorted(n for n in names if n.startswith(f"{args.split}/labels/") and n.endswith(".txt"))
        for label_name in label_names:
            rows = [r for r in z.read(label_name).decode("utf-8").splitlines() if r.strip()]
            image_name = label_name.replace(f"{args.split}/labels/", f"{args.split}/images/").replace(".txt", ".jpg")
            if image_name not in names:
                continue
            with z.open(image_name) as f:
                image_size = Image.open(f).size
            for row in rows:
                cls, bbox = yolo_to_xyxy(row, image_size)
                counts[str(cls)] += 1
                if 0 <= cls < len(CLASS_NAMES_EN):
                    by_class[cls].append((image_name, label_name, bbox))

        missing = [i for i in range(len(CLASS_NAMES_EN)) if not by_class[i]]
        if missing:
            raise SystemExit(f"Missing class ids in {args.split}: {missing}")

        thumbs = []
        for cls in range(len(CLASS_NAMES_EN)):
            items = by_class[cls][:]
            random.shuffle(items)
            for image_name, label_name, bbox in items[: args.per_class]:
                with z.open(image_name) as f:
                    img = Image.open(f).convert("RGB").resize((260, 260))
                scale_x = 260 / 416
                scale_y = 260 / 416
                x1, y1, x2, y2 = bbox
                box = [x1 * scale_x, y1 * scale_y, x2 * scale_x, y2 * scale_y]
                draw = ImageDraw.Draw(img)
                draw.rectangle(box, outline="red", width=3)
                label = f"{cls}: {CLASS_NAMES_EN[cls]}"
                draw.rectangle([0, 0, 126, 22], fill="white")
                draw.text((4, 4), label, fill="red")
                thumbs.append(img)

    cols = args.per_class
    rows = len(CLASS_NAMES_EN)
    grid = Image.new("RGB", (cols * 260, rows * 260), "white")
    for i, img in enumerate(thumbs):
        grid.paste(img, ((i % cols) * 260, (i // cols) * 260))

    grid_path = out_dir / f"{args.split}_label_mapping_grid.jpg"
    grid.save(grid_path, quality=92)

    summary = {
        "split": args.split,
        "class_names_en": CLASS_NAMES_EN,
        "class_names_ar": CLASS_NAMES_AR,
        "object_counts": dict(sorted(counts.items())),
        "grid": str(grid_path),
    }
    summary_path = out_dir / f"{args.split}_label_mapping_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

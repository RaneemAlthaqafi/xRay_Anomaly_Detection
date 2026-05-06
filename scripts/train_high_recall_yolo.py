from __future__ import annotations

import argparse
import shutil
import zipfile
from collections import Counter
from pathlib import Path

from ultralytics import YOLO


CLASS_NAMES = ["gun", "knife", "pliers", "scissors", "wrench"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a stronger high-recall YOLO model for baggage X-ray screening.")
    parser.add_argument("--zip", default="data/raw/xray-baggage.zip", help="Roboflow/Kaggle dataset zip.")
    parser.add_argument("--workdir", default="data/yolo/xray-baggage", help="Extracted dataset folder.")
    parser.add_argument("--model", default="yolo11m.pt", help="Use yolo11m.pt or yolo11l.pt for better quality.")
    parser.add_argument("--epochs", type=int, default=180)
    parser.add_argument("--imgsz", type=int, default=832)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default=0, help="GPU id, or cpu.")
    parser.add_argument("--project", default="runs/detect")
    parser.add_argument("--name", default="train_high_recall")
    parser.add_argument("--export", action="store_true", help="Export best.pt to ONNX after training.")
    return parser.parse_args()


def extract_dataset(zip_path: Path, workdir: Path) -> None:
    data_yaml = workdir / "data.yaml"
    if data_yaml.exists():
        return

    workdir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(workdir)


def rewrite_yaml(workdir: Path) -> Path:
    data_yaml = workdir / "data.yaml"
    yaml = "\n".join([
        f"path: {workdir.resolve()}",
        "train: train/images",
        "val: valid/images",
        "test: test/images",
        f"nc: {len(CLASS_NAMES)}",
        f"names: {CLASS_NAMES}",
        "",
    ])
    data_yaml.write_text(yaml, encoding="utf-8")
    return data_yaml


def count_labels(workdir: Path) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = {}
    for split in ["train", "valid", "test"]:
        split_counts: Counter[str] = Counter()
        for label_path in (workdir / split / "labels").glob("*.txt"):
            for row in label_path.read_text(encoding="utf-8").splitlines():
                if row.strip():
                    split_counts[row.split()[0]] += 1
        counts[split] = split_counts
    return {split: dict(sorted(counter.items())) for split, counter in counts.items()}


def assert_model_names(model: YOLO) -> None:
    names = getattr(model, "names", None)
    if isinstance(names, dict):
        actual = [str(names[i]) for i in range(len(CLASS_NAMES))]
    elif isinstance(names, list):
        actual = [str(v) for v in names[: len(CLASS_NAMES)]]
    else:
        actual = []
    if actual != CLASS_NAMES:
        raise SystemExit(f"Model class names mismatch. Expected {CLASS_NAMES}, got {actual}")


def main() -> None:
    args = parse_args()
    zip_path = Path(args.zip)
    workdir = Path(args.workdir)
    if not zip_path.exists():
        raise SystemExit(f"Dataset zip not found: {zip_path}")

    extract_dataset(zip_path, workdir)
    data_yaml = rewrite_yaml(workdir)
    print("Dataset label counts:", count_labels(workdir))

    model = YOLO(args.model)
    results = model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        optimizer="AdamW",
        lr0=0.0008,
        lrf=0.01,
        patience=35,
        cos_lr=True,
        cache="disk",
        rect=True,
        multi_scale=True,
        # X-ray colors encode material. Avoid HSV jitter that corrupts the signal.
        hsv_h=0.0,
        hsv_s=0.0,
        hsv_v=0.0,
        degrees=4.0,
        translate=0.08,
        scale=0.35,
        fliplr=0.5,
        flipud=0.0,
        mosaic=0.25,
        mixup=0.0,
        copy_paste=0.0,
        close_mosaic=25,
        project=args.project,
        name=args.name,
        exist_ok=True,
        plots=True,
        verbose=True,
    )

    run_dir = Path(results.save_dir)
    best_pt = run_dir / "weights" / "best.pt"
    if not best_pt.exists():
        raise SystemExit(f"Training finished but best.pt was not found at {best_pt}")

    best = YOLO(str(best_pt))
    assert_model_names(best)
    metrics = best.val(data=str(data_yaml), imgsz=args.imgsz, batch=args.batch, device=args.device, plots=True)
    print(f"mAP@0.5: {metrics.box.map50:.4f}")
    print(f"mAP@0.5:0.95: {metrics.box.map:.4f}")
    print(f"Precision: {metrics.box.mp:.4f}")
    print(f"Recall: {metrics.box.mr:.4f}")

    weights_dir = Path("data/weights")
    weights_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best_pt, weights_dir / "best.pt")

    if args.export:
        onnx_path = best.export(format="onnx", imgsz=args.imgsz, opset=12, simplify=True, dynamic=False)
        shutil.copy2(onnx_path, weights_dir / "best.onnx")
        print(f"Exported ONNX to {weights_dir / 'best.onnx'}")


if __name__ == "__main__":
    main()

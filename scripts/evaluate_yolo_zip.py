from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from ultralytics import YOLO


CLASS_NAMES = ["gun", "knife", "pliers", "scissors", "wrench"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate YOLO weights on the zipped baggage X-ray dataset.")
    parser.add_argument("--model", default="data/weights/best.onnx")
    parser.add_argument("--zip", default="data/raw/xray-baggage.zip")
    parser.add_argument("--workdir", default="data/yolo/xray-baggage")
    parser.add_argument("--split", default="test", choices=["train", "valid", "test"])
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.001)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--allow-name-mismatch", action="store_true")
    return parser.parse_args()


def prepare_dataset(zip_path: Path, workdir: Path) -> Path:
    data_yaml = workdir / "data.yaml"
    if not data_yaml.exists():
        workdir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(workdir)

    data_yaml.write_text(
        "\n".join([
            f"path: {workdir.resolve()}",
            "train: train/images",
            "val: valid/images",
            "test: test/images",
            f"nc: {len(CLASS_NAMES)}",
            f"names: {CLASS_NAMES}",
            "",
        ]),
        encoding="utf-8",
    )
    return data_yaml


def model_names(model: YOLO) -> list[str]:
    names = getattr(model, "names", None)
    if isinstance(names, dict):
        return [str(names[i]) for i in range(len(CLASS_NAMES))]
    if isinstance(names, list):
        return [str(v) for v in names[: len(CLASS_NAMES)]]
    return []


def main() -> None:
    args = parse_args()
    data_yaml = prepare_dataset(Path(args.zip), Path(args.workdir))
    model = YOLO(args.model, task="detect")
    actual_names = model_names(model)
    if actual_names != CLASS_NAMES and not args.allow_name_mismatch:
        raise SystemExit(f"Model class names mismatch. Expected {CLASS_NAMES}, got {actual_names}")
    metrics = model.val(
        data=str(data_yaml),
        split=args.split,
        imgsz=args.imgsz,
        conf=args.conf,
        batch=args.batch,
        plots=True,
        project="runs/evaluate",
        name=f"{Path(args.model).stem}_{args.split}",
        exist_ok=True,
    )

    summary = {
        "split": args.split,
        "model": args.model,
        "class_names": actual_names,
        "map50": round(float(metrics.box.map50), 4),
        "map50_95": round(float(metrics.box.map), 4),
        "precision": round(float(metrics.box.mp), 4),
        "recall": round(float(metrics.box.mr), 4),
        "classes": {
            name: round(float(metrics.box.ap50[i]), 4)
            for i, name in enumerate(CLASS_NAMES)
            if i < len(metrics.box.ap50)
        },
    }
    out_dir = Path(metrics.save_dir)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Plots saved to {out_dir}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply Colab training artifacts to the local web app.")
    parser.add_argument("artifact_zip", help="Path to xray_model_artifacts_for_app.zip from Colab.")
    parser.add_argument("--weights-dir", default="data/weights")
    parser.add_argument("--demo-dir", default="services/web/public/demo")
    parser.add_argument("--runs-dir", default="runs/colab_import")
    return parser.parse_args()


def copy_required(src_root: Path, relative: str, dest: Path) -> None:
    src = src_root / relative
    if not src.exists():
        raise SystemExit(f"Missing required artifact: {relative}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"Copied {src} -> {dest}")


def replace_dir(src: Path, dest: Path) -> None:
    if not src.exists():
        print(f"Skipping missing optional folder: {src}")
        return
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    print(f"Copied {src} -> {dest}")


def main() -> None:
    args = parse_args()
    artifact_zip = Path(args.artifact_zip)
    if not artifact_zip.exists():
        raise SystemExit(f"Artifact zip not found: {artifact_zip}")

    import_root = Path(args.runs_dir)
    if import_root.exists():
        shutil.rmtree(import_root)
    import_root.mkdir(parents=True)

    with zipfile.ZipFile(artifact_zip) as z:
        z.extractall(import_root)

    root = import_root / "artifacts_for_app"
    if not root.exists():
        raise SystemExit("Expected folder artifacts_for_app/ inside the zip.")

    weights_dir = Path(args.weights_dir)
    copy_required(root, "best.onnx", weights_dir / "best.onnx")
    if (root / "best.pt").exists():
        shutil.copy2(root / "best.pt", weights_dir / "best.pt")
        print(f"Copied {root / 'best.pt'} -> {weights_dir / 'best.pt'}")

    replace_dir(root / "demo", Path(args.demo_dir))
    replace_dir(root / "evaluate", import_root / "evaluate")
    replace_dir(root / "audit", import_root / "audit")

    print("\nArtifacts applied. Rebuild with:")
    print("  docker compose up -d --build")


if __name__ == "__main__":
    main()

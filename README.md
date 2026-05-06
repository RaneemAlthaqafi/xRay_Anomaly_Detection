# X-Ray Baggage Anomaly Detection: Saudi Ports

YOLOv11-based detector for 5 prohibited item classes in baggage X-ray scans, with an Arabic-first RTL web UI for port security officers.

| # | Class (EN) | الفئة |
|---|---|---|
| 0 | gun | مسدس |
| 1 | knife | سكين |
| 2 | pliers | كماشة |
| 3 | scissors | مقص |
| 4 | wrench | مفتاح ربط |

**Stack:** FastAPI + Ultralytics YOLOv11 backend • Next.js 15 + shadcn/ui frontend (RTL) • Docker Compose orchestration.

---

## Architecture (M1)

```
                ┌──────────────┐       POST /api/detect
                │   Browser    │  ──────────────────────▶  ┌─────────────┐
                │  Next.js 15  │                           │   FastAPI   │
                │   (RTL/AR)   │  ◀──────────────────────  │  + YOLOv11  │
                └──────────────┘   JSON + base64 image     └─────────────┘
                                                                  │
                                                                  ▼
                                                           best.pt (weights)
```

---

## Quickstart

### Prerequisites
- Docker + Docker Compose
- Trained model weights at `data/weights/best.pt` (train on Kaggle via [notebooks/01_train_yolov11s.ipynb](notebooks/01_train_yolov11s.ipynb))

### Run
```bash
cp .env.example .env
docker compose up --build
```

Then open:
- UI: http://localhost:3000
- API docs (Swagger): http://localhost:8000/docs

---

## Repository layout

```
xRay_Detection/
├── data/                    # Data & weights (gitignored)
│   ├── raw/
│   ├── yolo/
│   └── weights/best.pt
├── notebooks/
│   └── 01_train_yolov11s.ipynb
├── services/
│   ├── api/                 # FastAPI + YOLO (inference)
│   └── web/                 # Next.js 15 + shadcn/ui (RTL)
├── docker-compose.yml
└── README.md
```

---

## Dataset

- Source: [Kaggle — orvile/x-ray-baggage-anomaly-detection](https://www.kaggle.com/datasets/orvile/x-ray-baggage-anomaly-detection)
- Training reference: [killa92/map-0-9-baggage-anomaly-detection-yolov11](https://www.kaggle.com/code/killa92/map-0-9-baggage-anomaly-detection-yolov11)

## Improving Model Quality

The current `best.onnx` is a runnable baseline. If detections look weak, do not try
to fix that in the UI; retrain a stronger model and validate it before replacing
production weights.

Ready hosted model option:

Roboflow Universe has a ready X-ray baggage model (`x-ray-baggage-rkyb4/3`) listed
with mAP@50 around 94%. To use it for a stronger client demo, set:

```bash
INFERENCE_PROVIDER=roboflow
ROBOFLOW_MODEL_ID=x-ray-baggage-rkyb4/3
ROBOFLOW_API_KEY=your_key_here
docker compose up -d --build
```

Colab workflow:

1. Open `notebooks/02_colab_train_high_recall.ipynb` in Colab with a GPU runtime.
2. Run the label-mapping cell first and visually confirm:
   `0=gun`, `1=knife`, `2=pliers`, `3=scissors`, `4=wrench`.
3. Train `yolo11m.pt` first. If the client demo still needs better separation
   between knife/pliers/scissors, rerun with `yolo11l.pt` or `yolo11x.pt`.
4. Download `xray_model_artifacts_for_app.zip`, copy `best.onnx` into
   `data/weights/`, copy the regenerated `demo/` folder into
   `services/web/public/demo/`, then rebuild.

Or apply the Colab zip automatically:

```bash
python scripts/apply_colab_artifacts.py xray_model_artifacts_for_app.zip
docker compose up -d --build
```

Recommended high-recall training, preferably on Kaggle/Colab with a GPU:

```bash
python scripts/train_high_recall_yolo.py --device 0 --model yolo11m.pt --epochs 180 --imgsz 832 --batch 8 --export
```

For a stronger but slower model:

```bash
python scripts/train_high_recall_yolo.py --device 0 --model yolo11l.pt --epochs 220 --imgsz 832 --batch 6 --export
```

Quickly audit the current model against bundled samples and compare confidence
thresholds:

```bash
python scripts/audit_model.py --model data/weights/best.onnx --images samples
```

For port-security screening, the API defaults to `CONF_THRESHOLD=0.20` to favor
recall and reduce missed threats. Raise it only after validation confirms false
positives are hurting operations more than missed detections.

## Results

| Metric | Target |
|---|---|
| mAP@0.5 | ≥ 0.85 |
| mAP@0.5:0.95 | TBD after training |
| Inference latency (CPU) | < 500 ms / image |

Updated after training runs.

---

## Roadmap

- **M1 (current):** training notebook + FastAPI sync inference + Next.js RTL UI.
- **M2:** async inference via Redis queue + worker service; SQLite history of scans.
- **M3:** JWT auth + roles, multi-tenant by port, MinIO storage, Prometheus metrics, Arabic PDF reports.

---

## License

Internal and educational use.

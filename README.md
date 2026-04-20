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

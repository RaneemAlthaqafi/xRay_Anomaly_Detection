# xRay Anomaly Detection — API (FastAPI)

Inference service for the X-ray baggage anomaly detector. Wraps an Ultralytics YOLOv11s model and renders Arabic-shaped labels on the returned image.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness probe |
| GET | `/api/classes` | Returns the 5 classes with AR/EN names |
| POST | `/api/detect` | Upload an image → annotated image (base64 PNG) + JSON detections |
| GET | `/docs` | Swagger UI (auto-generated) |

## Run locally (without Docker)

```bash
cd services/api
python -m venv .venv && source .venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt

# Put trained weights at ../../data/weights/best.pt, then:
export MODEL_PATH=../../data/weights/best.pt
export FONT_PATH=./fonts/NotoNaskhArabic-Regular.ttf
uvicorn app.main:app --reload --port 8000
```

## Smoke test

```bash
curl -F "image=@sample.jpg" http://localhost:8000/api/detect | jq .detections
```

## Tests

```bash
pytest -v
```

Model-dependent tests auto-skip when `best.pt` is absent.

## Arabic rendering

`cv2.putText` does not shape Arabic. We use `arabic_reshaper` + `python-bidi` + PIL with a bundled Noto Naskh font ([app/annotate_ar.py](app/annotate_ar.py)). The font file must be present at `services/api/fonts/NotoNaskhArabic-Regular.ttf` — download from [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Naskh+Arabic) and place it there before the first build.

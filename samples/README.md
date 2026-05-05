# Sample Test Images

15 X-ray baggage images (3 per class) extracted from the test split of the project's source dataset, included here so anyone cloning the repo can immediately try the detector through the UI without setting up Kaggle.

## Source

- Dataset: [orvile/x-ray-baggage-anomaly-detection](https://www.kaggle.com/datasets/orvile/x-ray-baggage-anomaly-detection) on Kaggle (mirror of [malek-mhnrl/x-ray-baggage-detection](https://universe.roboflow.com/malek-mhnrl/x-ray-baggage-detection) on Roboflow Universe).
- License: **CC BY 4.0** — you may share and adapt with attribution to the original creator.
- Selection: 3 images per class (gun, knife, pliers, scissors, wrench) chosen with `random.seed(42)` from the 883 test images, biasing toward images with at least one of the target classes.

## How to use

1. Start the system: `docker compose up -d`
2. Open http://localhost:3030
3. Drag any `.jpg` from this folder into the upload area.
4. The annotated image and detection table appear within a second.

## Quick spot-check (already verified once)

| File | Detected | Confidence |
|---|---|---|
| `017261_jpg.rf.6b3ace7…` | gun | 66% |
| `020350_jpg.rf.141c30c…` | gun | 68% |
| `021668_jpg.rf.254a8c5…` | gun | 70% |
| `028986_jpg.rf.79a0df8…` | wrench | 55% |
| `009688_jpg.rf.6779a4f…` | pliers | 41% |
| `009426_jpg.rf.7948112…` | scissors | 38% |

Inference latency on the host (CPU, Docker): ~150–330 ms per image after warmup.

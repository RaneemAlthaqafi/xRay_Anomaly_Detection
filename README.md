<div dir="rtl">

# نظام كشف التهديدات في حقائب الأشعة السينية — الموانئ السعودية

نظام ذكاء اصطناعي للكشف عن العناصر الممنوعة في صور الأشعة السينية لحقائب المسافرين والشحنات. يعتمد على نموذج **YOLOv11** مدرَّب للتعرف على خمس فئات من التهديدات:

| # | الفئة | English |
|---|---|---|
| 0 | مسدس | gun |
| 1 | سكين | knife |
| 2 | كماشة | pliers |
| 3 | مقص | scissors |
| 4 | مفتاح ربط | wrench |

الواجهة عربية أصيلة (RTL) وتدعم الإنجليزية كلغة ثانوية، مصمَّمة لاستخدام ضباط الأمن في الموانئ السعودية.

---

## المعمارية (الإصدار الحالي — M1)

```
                ┌──────────────┐       POST /api/detect
                │   متصفح      │  ──────────────────────▶  ┌─────────────┐
                │  Next.js 15  │                           │   FastAPI   │
                │  (RTL عربي)  │  ◀──────────────────────  │  + YOLOv11  │
                └──────────────┘   JSON + base64 image     └─────────────┘
                                                                  │
                                                                  ▼
                                                           best.pt (weights)
```

**المرحلة الثانية (M2):** إضافة طابور Redis + Worker منفصل + قاعدة بيانات SQLite لسجل الفحوصات — على نفس نمط مشروع [Baseer_ZATCA](https://github.com/bahyali/Baseer_ZATCA).

**المرحلة الثالثة (M3):** مصادقة JWT، تعدد المستأجرين، تخزين MinIO، مراقبة Prometheus، تقارير PDF عربية.

---

## البدء السريع

### المتطلبات
- Docker + Docker Compose
- ملفات أوزان النموذج في `data/weights/best.pt` (دُرِّبت على Kaggle — انظر [notebooks/01_train_yolov11s.ipynb](notebooks/01_train_yolov11s.ipynb))

### التشغيل
```bash
cp .env.example .env
docker compose up --build
```

ثم افتح:
- الواجهة: http://localhost:3000
- توثيق الـ API (Swagger): http://localhost:8000/docs

---

## هيكل المستودع

```
xRay_Detection/
├── data/                    # البيانات والأوزان (مُستبعَد من Git)
│   ├── raw/
│   ├── yolo/
│   └── weights/best.pt
├── notebooks/
│   └── 01_train_yolov11s.ipynb
├── services/
│   ├── api/                 # FastAPI + YOLO (الاستدلال)
│   └── web/                 # Next.js 15 + shadcn/ui (واجهة RTL)
├── docker-compose.yml
└── README.md
```

---

## البيانات

مصدر البيانات: [Kaggle — orvile/x-ray-baggage-anomaly-detection](https://www.kaggle.com/datasets/orvile/x-ray-baggage-anomaly-detection).
مرجع التدريب: [killa92/map-0-9-baggage-anomaly-detection-yolov11](https://www.kaggle.com/code/killa92/map-0-9-baggage-anomaly-detection-yolov11).

## النتائج

| المقياس | القيمة المستهدفة |
|---|---|
| mAP@0.5 | ≥ 0.85 |
| mAP@0.5:0.95 | سيُحدَّث بعد التدريب |
| زمن الاستدلال (CPU) | < 500 مللي ثانية لكل صورة |

تُحدَّث بعد تشغيل notebook التدريب.

---

## الرخصة

للاستخدام الداخلي والتعليمي.

</div>

---

<details>
<summary>🇬🇧 English summary</summary>

# X-Ray Baggage Anomaly Detection — Saudi Ports

YOLOv11-based detector for 5 prohibited item classes (gun, knife, pliers, scissors, wrench) in baggage X-ray scans, with an Arabic-first RTL web UI for port security officers.

**Stack:** FastAPI + Ultralytics YOLOv11 backend • Next.js 15 + shadcn/ui frontend • Docker Compose orchestration.

**Quickstart:**
```bash
cp .env.example .env
docker compose up --build
```
Open http://localhost:3000 (UI) or http://localhost:8000/docs (API).

Training: see [notebooks/01_train_yolov11s.ipynb](notebooks/01_train_yolov11s.ipynb) (runs on Kaggle with free GPU).

Roadmap: M1 (MVP, current) → M2 (async Redis queue + SQLite, mirroring [Baseer_ZATCA](https://github.com/bahyali/Baseer_ZATCA)) → M3 (auth, multi-tenant, production hardening).

</details>

# xRay Anomaly Detection — Web (Next.js 15)

Arabic-first (RTL) operator UI. Uploads an X-ray image → calls the FastAPI backend → renders the annotated image and a detection table.

## Stack
- Next.js 15 (App Router) + React 19
- TypeScript
- Tailwind CSS
- next-intl (locales: `ar` default, `en` fallback)
- Cairo (Arabic) + Inter (Latin) via `next/font/google`

## Run locally
```bash
cd services/web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```
Open http://localhost:3000 (Arabic, RTL). Switch to English at http://localhost:3000/en or click the language toggle.

## Build for production
```bash
npm run build
NEXT_PUBLIC_API_URL=http://localhost:8000 npm start
```

The Dockerfile uses Next.js `output: "standalone"` for a small runtime image.

## Folder layout
```
app/
├── layout.tsx              # root (minimal — locale-aware html lives below)
└── [locale]/
    ├── layout.tsx          # sets <html lang dir>, loads fonts, intl provider
    └── page.tsx            # main upload + result view
components/
├── UploadDropzone.tsx
├── DetectionResult.tsx
├── LocaleSwitcher.tsx
└── ui/                     # Button, Card, Badge (shadcn-style, hand-rolled)
i18n/
├── routing.ts              # next-intl routing config
└── request.ts              # server-side messages loader
lib/
├── api.ts                  # fetch wrapper for /api/detect
└── utils.ts                # cn() helper
messages/
├── ar.json
└── en.json
middleware.ts               # next-intl locale negotiation
```

export type Severity = "high" | "medium" | "low";

export interface Detection {
  class_id: number;
  class_name_en: string;
  class_name_ar: string;
  severity: Severity;
  confidence: number;
  bbox: [number, number, number, number];
}

export interface DetectResponse {
  detections: Detection[];
  annotated_image_b64: string;
  image_width: number;
  image_height: number;
  inference_ms: number;
  model_name: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function detectImage(file: File): Promise<DetectResponse> {
  const form = new FormData();
  form.append("image", file);

  const res = await fetch(`${API_BASE}/api/detect`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API error ${res.status}: ${text || res.statusText}`);
  }

  return res.json();
}

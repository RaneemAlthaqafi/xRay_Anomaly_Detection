"use client";

import { useTranslations } from "next-intl";
import { CheckCircle2, AlertTriangle, RotateCcw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { SeverityBadge } from "@/components/ui/Badge";
import type { DetectResponse } from "@/lib/api";

function formatBbox(bbox: [number, number, number, number]) {
  const [x1, y1, x2, y2] = bbox.map(Math.round);
  return `${x1}, ${y1} → ${x2}, ${y2}`;
}

export function DetectionResult({
  result,
  locale,
  onReset,
}: {
  result: DetectResponse;
  locale: "ar" | "en";
  onReset: () => void;
}) {
  const t = useTranslations("results");
  const tSev = useTranslations("severity");
  const tUp = useTranslations("upload");
  const isAr = locale === "ar";

  const count = result.detections.length;
  const headline =
    count === 0
      ? t("no_detections")
      : count === 1
        ? t("found_one")
        : count === 2
          ? t("found_two")
          : t("found", { count });

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
      <Card className="lg:col-span-3">
        <CardHeader className="flex flex-row items-center justify-between gap-3">
          <CardTitle>{t("image_label")}</CardTitle>
          <Button variant="ghost" size="sm" onClick={onReset}>
            <RotateCcw className="h-4 w-4" />
            {tUp("reset")}
          </Button>
        </CardHeader>
        <CardContent>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={`data:image/png;base64,${result.annotated_image_b64}`}
            alt={t("image_label")}
            className="w-full rounded-lg border border-slate-200"
          />
          <dl className="mt-4 grid grid-cols-2 gap-2 text-sm text-slate-600 sm:grid-cols-3">
            <div>{t("inference_time", { ms: result.inference_ms.toFixed(0) })}</div>
            <div>{t("image_size", { w: result.image_width, h: result.image_height })}</div>
            <div className="truncate">{t("model_name", { name: result.model_name })}</div>
          </dl>
        </CardContent>
      </Card>

      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>{t("details")}</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className={`mb-5 flex items-start gap-3 rounded-xl p-4 ${
              count === 0
                ? "bg-emerald-50 text-emerald-900 ring-1 ring-emerald-200"
                : "bg-amber-50 text-amber-900 ring-1 ring-amber-200"
            }`}
          >
            {count === 0 ? (
              <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600" />
            ) : (
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
            )}
            <div>
              <div className="font-bold">{headline}</div>
              {count === 0 && (
                <div className="mt-1 text-sm opacity-80">{t("no_detections_hint")}</div>
              )}
            </div>
          </div>

          {count > 0 && (
            <div className="overflow-hidden rounded-lg ring-1 ring-slate-200">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-slate-700">
                  <tr>
                    <th className="px-3 py-2 text-start font-bold">{t("table_class")}</th>
                    <th className="px-3 py-2 text-start font-bold">{t("table_confidence")}</th>
                    <th className="px-3 py-2 text-start font-bold">{t("table_severity")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {result.detections.map((d, i) => (
                    <tr key={i} className="bg-white">
                      <td className="px-3 py-2.5 font-medium text-slate-900">
                        {isAr ? d.class_name_ar : d.class_name_en}
                      </td>
                      <td className="px-3 py-2.5 text-slate-700">
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-200">
                            <div
                              className="h-full bg-brand-600"
                              style={{ width: `${d.confidence * 100}%` }}
                            />
                          </div>
                          <span className="tabular-nums">
                            {(d.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-3 py-2.5">
                        <SeverityBadge severity={d.severity} label={tSev(d.severity)} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

"use client";

import { useTranslations } from "next-intl";
import { AlertTriangle, CheckCircle2, ClipboardCheck, RotateCcw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { SeverityBadge } from "@/components/ui/Badge";
import type { DetectResponse } from "@/lib/api";

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
  const tRisk = useTranslations("risk");
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

  const riskClasses =
    result.risk_level === "high"
      ? "bg-red-50 text-red-900 ring-red-200"
      : result.risk_level === "medium"
        ? "bg-amber-50 text-amber-900 ring-amber-200"
        : "bg-emerald-50 text-emerald-900 ring-emerald-200";

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
      <Card className="lg:col-span-3">
        <CardHeader className="flex flex-row items-center justify-between gap-3">
          <CardTitle>{t("image_label")}</CardTitle>
          <Button variant="ghost" size="sm" onClick={onReset} aria-label={tUp("reset")}>
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
          <dl className="mt-4 grid grid-cols-1 gap-2 text-sm text-slate-600 sm:grid-cols-3">
            <div>{t("image_size", { w: result.image_width, h: result.image_height })}</div>
            <div>{t("items_count", { count })}</div>
            <div>{tRisk(result.risk_level)}</div>
          </dl>
        </CardContent>
      </Card>

      <section className="space-y-6 lg:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle>{t("decision")}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`rounded-lg p-4 ring-1 ${riskClasses}`}>
              <div className="flex items-start gap-3">
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
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-slate-50 p-3 ring-1 ring-slate-200">
                <div className="text-xs text-slate-500">{t("risk_score")}</div>
                <div className="mt-1 text-2xl font-extrabold text-slate-950">
                  {result.risk_score}
                </div>
              </div>
              <div className="rounded-lg bg-slate-50 p-3 ring-1 ring-slate-200">
                <div className="text-xs text-slate-500">{t("priority")}</div>
                <div className="mt-2 text-sm font-bold text-slate-950">
                  {tRisk(result.inspection_priority)}
                </div>
              </div>
            </div>

            <div className="mt-4 flex gap-3 rounded-lg bg-slate-900 p-4 text-white">
              <ClipboardCheck className="mt-0.5 h-5 w-5 shrink-0 text-teal-300" />
              <div>
                <div className="text-xs font-semibold uppercase text-slate-300">
                  {t("recommended_action")}
                </div>
                <p className="mt-1 text-sm leading-6">
                  {isAr ? result.recommended_action_ar : result.recommended_action_en}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("details")}</CardTitle>
          </CardHeader>
          <CardContent>
            {count > 0 ? (
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
                          {d.class_name_en}
                        </td>
                        <td className="px-3 py-2.5 text-slate-700">
                          <div className="flex items-center gap-2">
                            <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-200">
                              <div
                                className="h-full bg-teal-600"
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
            ) : (
              <p className="text-sm leading-6 text-slate-600">{t("no_detections_hint")}</p>
            )}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}

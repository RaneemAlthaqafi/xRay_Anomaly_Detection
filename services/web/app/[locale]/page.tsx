"use client";

import { useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { BadgeCheck, FileImage, ShieldCheck, SearchCheck } from "lucide-react";
import { UploadDropzone } from "@/components/UploadDropzone";
import { DetectionResult } from "@/components/DetectionResult";
import { LocaleSwitcher } from "@/components/LocaleSwitcher";
import { detectImage, type DetectResponse } from "@/lib/api";

const demoImages = [
  { file: "0-scissors.jpg", label: "Scissors" },
  { file: "1-gun.jpg", label: "Gun" },
  { file: "2-knife.jpg", label: "Knife" },
  { file: "3-wrench.jpg", label: "Wrench" },
  { file: "4-pliers.jpg", label: "Pliers" },
];

export default function HomePage() {
  const t = useTranslations("app");
  const tFooter = useTranslations("footer");
  const tUp = useTranslations("upload");
  const locale = useLocale() as "ar" | "en";

  const [result, setResult] = useState<DetectResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [networkError, setNetworkError] = useState<string | null>(null);

  async function handleSelected(file: File) {
    setLoading(true);
    setNetworkError(null);
    setResult(null);
    try {
      const r = await detectImage(file);
      setResult(r);
    } catch (e) {
      console.error(e);
      setNetworkError(tUp("error_network"));
    } finally {
      setLoading(false);
    }
  }

  async function handleDemo(fileName: string) {
    const response = await fetch(`/demo/${fileName}`);
    const blob = await response.blob();
    const file = new File([blob], fileName, { type: blob.type || "image/jpeg" });
    await handleSelected(file);
  }

  const steps = [
    { icon: FileImage, label: t("step_upload"), value: t("step_upload_hint"), tone: "text-slate-700 bg-slate-100" },
    { icon: SearchCheck, label: t("step_review"), value: t("step_review_hint"), tone: "text-amber-700 bg-amber-50" },
    { icon: BadgeCheck, label: t("step_action"), value: t("step_action_hint"), tone: "text-emerald-700 bg-emerald-50" },
  ];

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 text-white">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-base font-extrabold leading-tight text-slate-950">
                {t("title")}
              </h1>
              <p className="text-xs text-slate-500">{t("subtitle")}</p>
            </div>
          </div>
          <LocaleSwitcher />
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-5 py-8 sm:px-6">
        {!result ? (
          <div className="grid gap-6 lg:grid-cols-[1fr_420px]">
            <section>
              <p className="mb-5 max-w-3xl text-lg leading-8 text-slate-700">
                {t("tagline")}
              </p>
              <UploadDropzone onSelected={handleSelected} isLoading={loading} />
              <div className="mt-5">
                <div className="mb-3 flex items-end justify-between gap-3">
                  <div>
                    <h2 className="text-sm font-extrabold text-slate-950">{t("demo_title")}</h2>
                    <p className="mt-1 text-xs text-slate-500">{t("demo_hint")}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
                  {demoImages.map((image) => (
                    <button
                      key={image.file}
                      type="button"
                      disabled={loading}
                      onClick={() => handleDemo(image.file)}
                      className="group overflow-hidden rounded-lg border border-slate-200 bg-white text-start shadow-sm transition hover:border-slate-400 disabled:pointer-events-none disabled:opacity-60"
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={`/demo/${image.file}`}
                        alt={image.label}
                        className="aspect-square w-full object-cover"
                      />
                      <span className="block px-2 py-2 text-xs font-bold text-slate-800">
                        {image.label}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
              {networkError && (
                <p className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-center text-sm text-red-700 ring-1 ring-red-200">
                  {networkError}
                </p>
              )}
            </section>

            <aside className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
              {steps.map(({ icon: Icon, label, value, tone }) => (
                <div key={label} className="rounded-lg border border-slate-200 bg-white p-4">
                  <div className="flex items-start gap-3">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${tone}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                        {label}
                      </div>
                      <div className="mt-1 text-sm font-bold text-slate-950">{value}</div>
                    </div>
                  </div>
                </div>
              ))}
            </aside>
          </div>
        ) : (
          <DetectionResult
            result={result}
            locale={locale}
            onReset={() => setResult(null)}
          />
        )}
      </div>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 text-xs text-slate-500 sm:px-6">
          <span>{tFooter("internal")}</span>
          <span>{tFooter("version")}</span>
        </div>
      </footer>
    </main>
  );
}

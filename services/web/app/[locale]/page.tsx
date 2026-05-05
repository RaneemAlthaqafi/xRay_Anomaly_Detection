"use client";

import { useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { ShieldCheck } from "lucide-react";
import { UploadDropzone } from "@/components/UploadDropzone";
import { DetectionResult } from "@/components/DetectionResult";
import { LocaleSwitcher } from "@/components/LocaleSwitcher";
import { detectImage, type DetectResponse } from "@/lib/api";

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

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-700 text-white">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-base font-extrabold leading-tight text-slate-900">
                {t("title")}
              </h1>
              <p className="text-xs text-slate-500">{t("subtitle")}</p>
            </div>
          </div>
          <LocaleSwitcher />
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-6 py-10">
        {!result ? (
          <div className="mx-auto max-w-2xl">
            <p className="mb-8 text-center text-lg text-slate-600">{t("tagline")}</p>
            <UploadDropzone onSelected={handleSelected} isLoading={loading} />
            {networkError && (
              <p className="mt-4 rounded-md bg-red-50 px-4 py-3 text-center text-sm text-red-700 ring-1 ring-red-200">
                {networkError}
              </p>
            )}
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
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 text-xs text-slate-500">
          <span>{tFooter("internal")}</span>
          <span>{tFooter("version")}</span>
        </div>
      </footer>
    </main>
  );
}

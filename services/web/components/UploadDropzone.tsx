"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { Upload, ImageIcon, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

const MAX_BYTES = 10 * 1024 * 1024;
const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];

export function UploadDropzone({
  onSelected,
  isLoading,
}: {
  onSelected: (file: File) => void;
  isLoading: boolean;
}) {
  const t = useTranslations("upload");
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const validate = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) return t("error_type");
    if (file.size > MAX_BYTES) return t("error_size");
    return null;
  };

  const handleFile = (file: File) => {
    const err = validate(file);
    if (err) {
      setError(err);
      return;
    }
    setError(null);
    onSelected(file);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        if (!isLoading) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        if (isLoading) return;
        const f = e.dataTransfer.files?.[0];
        if (f) handleFile(f);
      }}
      className={cn(
        "relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-12 transition-all",
        isDragging
          ? "border-brand-600 bg-brand-50"
          : "border-slate-300 bg-slate-50 hover:border-brand-400 hover:bg-brand-50/40",
        isLoading && "pointer-events-none opacity-70",
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ALLOWED_TYPES.join(",")}
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) handleFile(f);
          e.target.value = "";
        }}
      />

      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-100 text-brand-700">
        {isLoading ? (
          <Loader2 className="h-8 w-8 animate-spin" />
        ) : (
          <ImageIcon className="h-8 w-8" />
        )}
      </div>

      <p className="mt-5 text-lg font-bold text-slate-900">
        {isLoading ? t("uploading") : t("drop_here")}
      </p>

      {!isLoading && (
        <>
          <p className="mt-1 text-sm text-slate-500">{t("or")}</p>
          <Button
            type="button"
            variant="primary"
            size="md"
            className="mt-3"
            onClick={() => inputRef.current?.click()}
          >
            <Upload className="h-4 w-4" />
            {t("browse")}
          </Button>
          <p className="mt-4 text-xs text-slate-500">{t("hint")}</p>
        </>
      )}

      {error && (
        <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 ring-1 ring-red-200">
          {error}
        </p>
      )}
    </div>
  );
}

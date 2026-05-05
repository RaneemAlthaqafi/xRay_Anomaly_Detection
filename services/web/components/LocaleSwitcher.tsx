"use client";

import { useLocale, useTranslations } from "next-intl";
import { Languages } from "lucide-react";
import { useRouter, usePathname } from "@/i18n/routing";
import { Button } from "@/components/ui/Button";

export function LocaleSwitcher() {
  const locale = useLocale();
  const t = useTranslations("language");
  const router = useRouter();
  const pathname = usePathname();

  const next = locale === "ar" ? "en" : "ar";

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={() => router.replace(pathname, { locale: next })}
    >
      <Languages className="h-4 w-4" />
      {t("switch_to")}
    </Button>
  );
}

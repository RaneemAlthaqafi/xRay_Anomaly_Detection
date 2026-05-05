import * as React from "react";
import { cn } from "@/lib/utils";
import type { Severity } from "@/lib/api";

const severityClasses: Record<Severity, string> = {
  high: "bg-red-100 text-red-800 ring-1 ring-red-200",
  medium: "bg-amber-100 text-amber-800 ring-1 ring-amber-200",
  low: "bg-emerald-100 text-emerald-800 ring-1 ring-emerald-200",
};

export function SeverityBadge({
  severity,
  label,
  className,
}: {
  severity: Severity;
  label: string;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-bold",
        severityClasses[severity],
        className,
      )}
    >
      {label}
    </span>
  );
}

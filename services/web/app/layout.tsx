import type { ReactNode } from "react";
import "./globals.css";

// The root layout is intentionally minimal — locale-aware <html> attributes
// (lang/dir) live in app/[locale]/layout.tsx.
export default function RootLayout({ children }: { children: ReactNode }) {
  return children;
}

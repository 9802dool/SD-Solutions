import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SD Solutions (SDS) — Evidence Analysis",
  description:
    "Upload police documents and evidence to assess strengths, weaknesses, bulletproofing, and King's Counsel cross-examination prep.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}

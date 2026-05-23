"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  loadLegalKb,
  searchLegalKb,
  type LegalKnowledgeBase,
  type LegalSectionRecord,
} from "@/lib/legal-kb";

export default function LegalLibraryPage() {
  const [kb, setKb] = useState<LegalKnowledgeBase | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<LegalSectionRecord[]>([]);

  useEffect(() => {
    loadLegalKb().then(setKb).catch(() => setKb(null));
  }, []);

  useEffect(() => {
    if (!kb) return;
    setResults(query.trim() ? searchLegalKb(kb, query) : kb.sections.slice(0, 20));
  }, [kb, query]);

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Link href="/" className="text-sm text-blue-400 hover:underline">
        ← Back to analyser
      </Link>
      <h1 className="mt-4 text-3xl font-bold">TT Legal Knowledge Base</h1>
      <p className="mt-2 text-[var(--muted)]">
        Trinidad & Tobago law summaries for SDS cross-reference. Upload new laws with{" "}
        <code className="text-blue-300">python -m legal_kb import</code>.
      </p>

      <input
        className="mt-6 w-full rounded-lg border border-[var(--border)] bg-[#0f172a] px-4 py-2"
        placeholder="Search laws (e.g. hearsay, DNA, disclosure)…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <div className="mt-6 space-y-4">
        {kb &&
          results.map((sec) => (
            <article
              key={sec.id}
              className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"
            >
              <p className="text-xs text-blue-300">
                {sec.citation} · {sec.sectionRef}
              </p>
              <h2 className="font-semibold">{sec.title}</h2>
              <p className="mt-1 text-xs text-[var(--muted)]">{sec.sourceTitle}</p>
              <p className="mt-2 text-sm">{sec.summary}</p>
              {sec.evidenceTags.length > 0 && (
                <p className="mt-2 text-xs text-[var(--muted)]">
                  Tags: {sec.evidenceTags.join(", ")}
                </p>
              )}
            </article>
          ))}
        {!kb && <p className="text-sm text-[var(--muted)]">Loading legal library…</p>}
      </div>
    </div>
  );
}

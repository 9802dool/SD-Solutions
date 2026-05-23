"use client";

import { useMemo, useState } from "react";
import { analyzeCase, reportToMarkdown } from "@/lib/analyzer";
import { getDemoDocuments } from "@/lib/demo-data";
import type { AnalysisReport } from "@/lib/types";

type Tab =
  | "documents"
  | "features"
  | "ml"
  | "gaps"
  | "strengths"
  | "weaknesses"
  | "actions"
  | "cross"
  | "export";

const bandColors: Record<string, string> = {
  STRONG: "text-green-400",
  DEVELOPING: "text-amber-400",
  AT_RISK: "text-red-400",
};

export function AnalyzerApp() {
  const [caseReference, setCaseReference] = useState("CR-2026-001");
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [tab, setTab] = useState<Tab>("documents");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const markdown = useMemo(
    () => (report ? reportToMarkdown(report) : ""),
    [report],
  );

  async function readFiles(files: FileList | null) {
    if (!files?.length) return;
    setBusy(true);
    setError("");
    try {
      const documents: Record<string, string> = {};
      for (const file of Array.from(files)) {
        const text = await file.text();
        documents[file.name] = text;
      }
      setReport(analyzeCase(documents, caseReference));
      setTab("documents");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to read files.");
    } finally {
      setBusy(false);
    }
  }

  function runDemo() {
    setError("");
    setReport(analyzeCase(getDemoDocuments(), caseReference));
    setTab("documents");
  }

  function downloadReport() {
    if (!report) return;
    const blob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${caseReference}-sds-report.md`;
    link.click();
    URL.revokeObjectURL(url);
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: "documents", label: "Documents" },
    { id: "features", label: "NLP features" },
    { id: "ml", label: "ML confidence" },
    { id: "gaps", label: "Conviction gaps" },
    { id: "strengths", label: "Strengths" },
    { id: "weaknesses", label: "Weaknesses" },
    { id: "actions", label: "Bulletproofing" },
    { id: "cross", label: "KC cross-examination" },
    { id: "export", label: "Export" },
  ];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
            SDS
          </p>
          <h1 className="text-3xl font-bold sm:text-4xl">SD Solutions</h1>
          <p className="mt-2 max-w-2xl text-[var(--muted)]">
            Rule-based legal evaluation + NLP feature extraction + weighted evidence
            scoring + Random Forest conviction confidence — with human oversight required.
          </p>
        </div>
        <div className="rounded-full border border-[var(--border)] bg-[var(--card)] px-4 py-2 text-sm text-[var(--muted)]">
          Analysis runs in your browser — files are not uploaded to a server.
        </div>
      </header>

      <div className="mb-6 space-y-3">
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-100">
          Decision-support only. Not legal advice. A qualified legal professional must
          review all NLP and ML outputs before court use.
        </div>
        {report && (
          <div className="rounded-xl border border-purple-500/30 bg-purple-500/10 p-4 text-sm text-purple-100">
            {report.biasNotice}
          </div>
        )}
      </div>

      <section className="mb-8 grid gap-4 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 sm:grid-cols-[1fr_auto]">
        <div>
          <label className="mb-2 block text-sm font-medium">Case / OC reference</label>
          <input
            value={caseReference}
            onChange={(e) => setCaseReference(e.target.value)}
            className="w-full rounded-lg border border-[var(--border)] bg-[#0f172a] px-4 py-2 outline-none focus:border-blue-500"
          />
        </div>
        <div className="flex flex-col gap-3 sm:justify-end">
          <label className="cursor-pointer rounded-lg bg-blue-600 px-5 py-2 text-center text-sm font-semibold hover:bg-blue-500">
            Upload documents (.txt, .md)
            <input
              type="file"
              accept=".txt,.md,text/plain,text/markdown"
              multiple
              className="hidden"
              onChange={(e) => readFiles(e.target.files)}
            />
          </label>
          <button
            type="button"
            onClick={runDemo}
            className="rounded-lg border border-[var(--border)] px-5 py-2 text-sm font-semibold hover:bg-white/5"
          >
            Run demo case
          </button>
        </div>
      </section>

      {busy && <p className="mb-4 text-sm text-[var(--muted)]">Analysing…</p>}
      {error && (
        <p className="mb-4 rounded-lg border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">
          {error}
        </p>
      )}

      {report && (
        <>
          <section className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Metric label="Composite score" value={`${report.readinessScore}/100`} />
            <Metric
              label="ML confidence"
              value={report.modelPrediction?.confidenceLabel ?? "—"}
            />
            <Metric label="Strengths" value={String(report.strengths.length)} />
            <Metric label="Conviction gaps" value={String(report.missingElements.length)} />
          </section>

          <div className="mb-4 rounded-xl border border-[var(--border)] bg-[#0f172a] p-4">
            <p className="text-sm">{report.summary}</p>
            <p className={`mt-2 text-sm font-semibold ${bandColors[report.readinessBand]}`}>
              Band: {report.readinessBand}
            </p>
          </div>

          <div className="mb-4 flex flex-wrap gap-2">
            {tabs.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setTab(item.id)}
                className={`rounded-full px-4 py-2 text-sm ${
                  tab === item.id
                    ? "bg-blue-600 text-white"
                    : "border border-[var(--border)] text-[var(--muted)] hover:bg-white/5"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>

          <section className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
            {tab === "features" &&
              report.extractedFeatures.map((feat) => (
                <div key={feat.name} className="mb-3 flex justify-between border-b border-[var(--border)] pb-3 last:mb-0">
                  <span className="text-sm">{feat.label}</span>
                  <span className="font-mono text-sm text-blue-300">{feat.value.toFixed(2)}</span>
                </div>
              ))}

            {tab === "ml" && report.modelPrediction && (
              <div className="space-y-4">
                <div className="rounded-lg border border-blue-500/30 bg-blue-500/10 p-4">
                  <p className="text-2xl font-bold">{report.modelPrediction.confidenceLabel}</p>
                  <p className="mt-1 text-sm text-[var(--muted)]">
                    Conviction probability: {(report.modelPrediction.convictionProbability * 100).toFixed(1)}%
                  </p>
                  <p className="mt-1 text-xs text-[var(--muted)]">
                    Model: {report.modelPrediction.modelName}
                  </p>
                </div>
                <p className="text-sm text-[var(--muted)]">
                  Weighted evidence engine composite: {report.compositeScore}/100
                </p>
                {report.weightedScores.map((ws) => (
                  <div key={ws.category} className="flex justify-between text-sm">
                    <span>{ws.category}</span>
                    <span className="font-mono">
                      {ws.weightedContribution >= 0 ? "+" : ""}
                      {ws.weightedContribution.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {tab === "gaps" &&
              (report.missingElements.length ? (
                report.missingElements.map((gap, i) => (
                  <div key={i} className="mb-3 rounded-lg border border-amber-500/30 bg-amber-500/10 p-4">
                    <p className="font-semibold">
                      [{gap.severity.toUpperCase()}] {gap.element}
                    </p>
                    <p className="mt-2 text-sm">{gap.detail}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-green-400">
                  No major conviction gaps detected in uploaded text (verify manually).
                </p>
              ))}

            {tab === "documents" &&
              report.documents.map((doc) => (
                <div key={doc.filename} className="mb-4 border-b border-[var(--border)] pb-4 last:mb-0 last:border-0">
                  <h3 className="font-semibold">{doc.filename}</h3>
                  <p className="text-sm text-[var(--muted)]">
                    {doc.wordCount} words · {doc.detectedTypes.join(", ")}
                  </p>
                </div>
              ))}

            {tab === "strengths" &&
              report.strengths.map((item, i) => (
                <div key={i} className="mb-3 rounded-lg border border-green-500/30 bg-green-500/10 p-4">
                  <p className="font-semibold">{item.title}</p>
                  <p className="text-sm text-[var(--muted)]">{item.category}</p>
                  <p className="mt-2 text-sm">{item.detail}</p>
                </div>
              ))}

            {tab === "weaknesses" &&
              report.weaknesses.map((item, i) => (
                <div key={i} className="mb-3 rounded-lg border border-red-500/30 bg-red-500/10 p-4">
                  <p className="font-semibold">
                    [{item.severity.toUpperCase()}] {item.title}
                  </p>
                  <p className="text-sm text-[var(--muted)]">{item.category}</p>
                  <p className="mt-2 text-sm">{item.detail}</p>
                </div>
              ))}

            {tab === "actions" &&
              report.recommendations.map((rec) => (
                <div key={rec.priority} className="mb-4 border-b border-[var(--border)] pb-4 last:mb-0 last:border-0">
                  <p className="font-semibold">
                    {rec.priority}. {rec.action}
                  </p>
                  <p className="mt-1 text-sm text-[var(--muted)]">{rec.rationale}</p>
                  <p className="mt-1 text-xs text-blue-300">Ref: {rec.legalAnchor}</p>
                </div>
              ))}

            {tab === "cross" &&
              report.crossExamination.map((q, i) => (
                <details key={i} className="mb-3 rounded-lg border border-[var(--border)] p-4">
                  <summary className="cursor-pointer font-semibold">
                    {i + 1}. {q.theme} — {q.targetWitness}
                  </summary>
                  <p className="mt-3 text-sm">
                    <span className="font-medium">Question:</span> {q.question}
                  </p>
                  <p className="mt-2 text-sm text-[var(--muted)]">
                    <span className="font-medium text-[var(--foreground)]">Purpose:</span>{" "}
                    {q.purpose}
                  </p>
                  <p className="mt-2 text-sm text-[var(--muted)]">
                    <span className="font-medium text-[var(--foreground)]">Follow-up:</span>{" "}
                    {q.followUp}
                  </p>
                </details>
              ))}

            {tab === "export" && (
              <div className="space-y-4">
                <button
                  type="button"
                  onClick={downloadReport}
                  className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold hover:bg-blue-500"
                >
                  Download markdown report
                </button>
                <pre className="max-h-96 overflow-auto rounded-lg bg-[#0f172a] p-4 text-xs whitespace-pre-wrap">
                  {markdown}
                </pre>
              </div>
            )}
          </section>
        </>
      )}

      {!report && !busy && (
        <p className="text-center text-sm text-[var(--muted)]">
          Upload case documents or run the demo to begin analysis.
        </p>
      )}

      <footer className="mt-10 text-center text-xs text-[var(--muted)]">
        SD Solutions (SDS) — decision-support only; not legal advice.
      </footer>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
      <p className="text-sm text-[var(--muted)]">{label}</p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
    </div>
  );
}

import {
  countPatternMatches,
  detectDocumentTypes,
  EVIDENCE_RULES,
} from "./evidence-rules";
import { generateCrossExamination, weaknessToSeverity } from "./kc-cross-exam";
import type { AnalysisReport, ReadinessBand, Recommendation } from "./types";

export const DISCLAIMER =
  "SD SOLUTIONS (SDS) — DECISION-SUPPORT ONLY. NOT LEGAL ADVICE. " +
  "All outputs require review by qualified legal counsel. " +
  "Do not rely on automated analysis for charging, disclosure, or court decisions.";

const PRIORITY: Record<string, number> = {
  "Disclosure and unused material": 1,
  "Exhibits and continuity": 2,
  "Identification evidence": 3,
  "Witness statements": 4,
  "Digital / cyber evidence": 5,
  "Expert / forensic evidence": 6,
  "Documentary / hearsay": 7,
  "Corroboration and consistency": 8,
};

function scoreToBand(score: number): ReadinessBand {
  if (score >= 75) return "STRONG";
  if (score >= 50) return "DEVELOPING";
  return "AT_RISK";
}

function renumber(items: Recommendation[]): Recommendation[] {
  return items.map((item, index) => ({ ...item, priority: index + 1 }));
}

export function analyzeCase(
  documents: Record<string, string>,
  caseReference = "UNASSIGNED",
): AnalysisReport {
  if (Object.keys(documents).length === 0) {
    throw new Error("At least one document is required.");
  }

  const combinedText = Object.values(documents).join("\n\n");
  const summaries = Object.entries(documents).map(([filename, text]) => {
    const detected = detectDocumentTypes(text);
    return {
      filename,
      kind: detected[0] ?? "General document",
      wordCount: text.split(/\s+/).filter(Boolean).length,
      detectedTypes: detected.length ? detected : ["General document"],
    };
  });

  const strengths: AnalysisReport["strengths"] = [];
  const weaknesses: AnalysisReport["weaknesses"] = [];
  const recommendations: Recommendation[] = [];
  const seenActions = new Set<string>();

  for (const rule of EVIDENCE_RULES) {
    const strengthHits = countPatternMatches(combinedText, rule.strengthPatterns);
    const weaknessHits = countPatternMatches(combinedText, rule.weaknessPatterns);

    if (strengthHits.length && strengthHits.length >= weaknessHits.length) {
      strengths.push({
        category: rule.category,
        title: rule.strengthTitle,
        detail: rule.strengthDetail,
        severity: "low",
        evidenceRefs: strengthHits.slice(0, 3),
      });
    } else if (weaknessHits.length) {
      weaknesses.push({
        category: rule.category,
        title: rule.weaknessTitle,
        detail: rule.weaknessDetail,
        severity: weaknessToSeverity(rule.weaknessTitle),
        evidenceRefs: weaknessHits.slice(0, 3),
      });
      if (!seenActions.has(rule.bulletproofAction)) {
        seenActions.add(rule.bulletproofAction);
        recommendations.push({
          priority: PRIORITY[rule.category] ?? 9,
          action: rule.bulletproofAction,
          rationale: rule.weaknessDetail,
          legalAnchor: rule.legalAnchor,
        });
      }
    } else {
      weaknesses.push({
        category: rule.category,
        title: `No clear signals for ${rule.category.toLowerCase()}`,
        detail: `The uploaded bundle does not mention standard indicators for ${rule.category.toLowerCase()}. Absence in text does not prove a gap in the real file — verify manually.`,
        severity: "medium",
        evidenceRefs: [],
      });
      const confirmAction = `Confirm on file: ${rule.bulletproofAction}`;
      if (!seenActions.has(confirmAction)) {
        seenActions.add(confirmAction);
        recommendations.push({
          priority: (PRIORITY[rule.category] ?? 9) + 1,
          action: confirmAction,
          rationale: "Checklist item not evidenced in uploaded text.",
          legalAnchor: rule.legalAnchor,
        });
      }
    }
  }

  recommendations.sort((a, b) => a.priority - b.priority);
  const crossExamination = generateCrossExamination(weaknesses);
  const readinessScore = Math.max(
    0,
    Math.min(100, 55 + strengths.length * 8 - weaknesses.length * 7),
  );
  const readinessBand = scoreToBand(readinessScore);
  const highWeaknesses = weaknesses.filter((w) => w.severity === "high").length;

  return {
    caseReference,
    documents: summaries,
    strengths,
    weaknesses,
    recommendations: renumber(recommendations),
    crossExamination,
    readinessBand,
    readinessScore,
    summary: `Case \`${caseReference}\`: ${Object.keys(documents).length} document(s) analysed. ${strengths.length} strength signal(s), ${weaknesses.length} weakness or gap signal(s) (${highWeaknesses} high severity). Overall readiness: ${readinessBand} (${readinessScore}/100). Use cross-examination questions to stress-test before trial.`,
    disclaimer: DISCLAIMER,
  };
}

export function reportToMarkdown(report: AnalysisReport): string {
  const lines = [
    `# SDS case analysis report — ${report.caseReference}`,
    "",
    report.summary,
    "",
    `**Readiness band:** ${report.readinessBand} (${report.readinessScore}/100)`,
    "",
    "## Documents analysed",
    ...report.documents.map(
      (d) =>
        `- **${d.filename}** (${d.wordCount} words) — ${d.detectedTypes.join(", ")}`,
    ),
    "",
    "## Strengths",
    ...report.strengths.map(
      (s) => `- **${s.title}** (${s.category}): ${s.detail}`,
    ),
    "",
    "## Weaknesses and gaps",
    ...report.weaknesses.map(
      (w) =>
        `- **[${w.severity.toUpperCase()}] ${w.title}** (${w.category}): ${w.detail}`,
    ),
    "",
    "## Bulletproofing recommendations",
    ...report.recommendations.map(
      (r) =>
        `${r.priority}. **${r.action}** — ${r.rationale} *(Ref: ${r.legalAnchor})*`,
    ),
    "",
    "## Anticipated King's Counsel cross-examination",
    ...report.crossExamination.flatMap((q, i) => [
      `### ${i + 1}. ${q.theme}`,
      `- **Target:** ${q.targetWitness}`,
      `- **Question:** ${q.question}`,
      `- **Purpose:** ${q.purpose}`,
      `- **Follow-up:** ${q.followUp}`,
      "",
    ]),
    "---",
    report.disclaimer,
  ];

  return lines.join("\n");
}

import {
  countPatternMatches,
  detectDocumentTypes,
  EVIDENCE_RULES,
} from "./evidence-rules";
import { extractFeatures } from "./features";
import { generateCrossExamination, weaknessToSeverity } from "./kc-cross-exam";
import { predictConvictionStrength } from "./ml-model";
import {
  BIAS_NOTICE,
  compositeScoreFromWeights,
  computeWeightedScores,
  detectMissingElements,
} from "./scoring";
import type { AnalysisReport, ReadinessBand, Recommendation } from "./types";

export const DISCLAIMER =
  "SD SOLUTIONS (SDS) — DECISION-SUPPORT ONLY. NOT LEGAL ADVICE. " +
  "All outputs require review by qualified legal counsel. " +
  "Do not rely on automated analysis, NLP extraction, or ML confidence scores " +
  "for charging, disclosure, or court decisions. Human professional review is mandatory.";

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
  const { vector, details: extractedFeatures } = extractFeatures(combinedText);
  const weightedScores = computeWeightedScores(vector);
  const missingElements = detectMissingElements(vector);
  const modelPrediction = predictConvictionStrength(vector);
  const compositeScore = compositeScoreFromWeights(weightedScores);

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

  for (const gap of missingElements) {
    recommendations.unshift({
      priority: 0,
      action: `Close conviction gap: ${gap.element}`,
      rationale: gap.detail,
      legalAnchor: "Prosecution case preparation — proof beyond reasonable doubt",
    });
  }

  recommendations.sort((a, b) => a.priority - b.priority);
  const crossExamination = generateCrossExamination(weaknesses);

  const ruleScore = Math.max(0, Math.min(100, 55 + strengths.length * 8 - weaknesses.length * 7));
  const readinessScore = Math.round((compositeScore + ruleScore) / 2);
  const readinessBand = scoreToBand(readinessScore);
  const highWeaknesses = weaknesses.filter((w) => w.severity === "high").length;
  const mlPct = modelPrediction.convictionProbability * 100;

  return {
    caseReference,
    documents: summaries,
    strengths,
    weaknesses,
    recommendations: renumber(recommendations),
    crossExamination,
    extractedFeatures,
    weightedScores,
    missingElements,
    modelPrediction,
    readinessBand,
    readinessScore,
    compositeScore,
    summary: `Case \`${caseReference}\`: ${Object.keys(documents).length} document(s) analysed. ML conviction confidence: ${modelPrediction.confidenceLabel} (${mlPct.toFixed(0)}%) via ${modelPrediction.modelName}. Composite evidence score: ${readinessScore}/100 (${readinessBand}). ${strengths.length} rule strength(s), ${weaknesses.length} weakness/gap signal(s) (${highWeaknesses} high). ${missingElements.length} potential conviction gap(s) flagged. Human review required.`,
    biasNotice: BIAS_NOTICE,
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
  ];

  if (report.modelPrediction) {
    lines.push(
      "",
      "## ML conviction confidence (supportive only)",
      `- **Label:** ${report.modelPrediction.confidenceLabel}`,
      `- **Probability:** ${(report.modelPrediction.convictionProbability * 100).toFixed(1)}%`,
      `- **Model:** ${report.modelPrediction.modelName}`,
      `- **Human oversight required:** Yes`,
    );
  }

  lines.push(
    "",
    "## NLP extracted features",
    ...report.extractedFeatures.map(
      (f) => `- **${f.label}:** ${f.value.toFixed(2)} (${f.source})`,
    ),
    "",
    "## Weighted evidence scores",
    ...report.weightedScores.map(
      (w) =>
        `- **${w.category}** (weight ${w.weight.toFixed(2)}): score ${w.score.toFixed(2)} → ${w.weightedContribution >= 0 ? "+" : ""}${w.weightedContribution.toFixed(2)}`,
    ),
  );

  if (report.missingElements.length) {
    lines.push(
      "",
      "## Missing conviction elements",
      ...report.missingElements.map(
        (g) => `- **[${g.severity.toUpperCase()}] ${g.element}:** ${g.detail}`,
      ),
    );
  }

  lines.push(
    "",
    "## Documents analysed",
    ...report.documents.map(
      (d) => `- **${d.filename}** (${d.wordCount} words) — ${d.detectedTypes.join(", ")}`,
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
    "",
    "## Bias and fairness notice",
    report.biasNotice,
    "",
    "---",
    report.disclaimer,
  );

  return lines.join("\n");
}

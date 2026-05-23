import {
  Document,
  HeadingLevel,
  Packer,
  Paragraph,
  TextRun,
} from "docx";
import type { AnalysisReport } from "./types";

function heading(text: string, level: (typeof HeadingLevel)[keyof typeof HeadingLevel]) {
  return new Paragraph({ text, heading: level });
}

function body(text: string) {
  return new Paragraph({ children: [new TextRun(text)] });
}

function bullet(label: string, detail: string) {
  return new Paragraph({
    children: [
      new TextRun({ text: `${label}: `, bold: true }),
      new TextRun(detail),
    ],
  });
}

function numbered(line: string) {
  return new Paragraph({ text: line });
}

export async function reportToDocxBlob(report: AnalysisReport): Promise<Blob> {
  const children: Paragraph[] = [
    heading(`SDS case analysis report — ${report.caseReference}`, HeadingLevel.HEADING_1),
    body(report.summary),
    body(`Readiness band: ${report.readinessBand} (${report.readinessScore}/100)`),
  ];

  if (report.modelPrediction) {
    children.push(
      heading("ML conviction confidence (supportive only)", HeadingLevel.HEADING_2),
      bullet("Label", report.modelPrediction.confidenceLabel),
      bullet(
        "Probability",
        `${(report.modelPrediction.convictionProbability * 100).toFixed(1)}%`,
      ),
      bullet("Model", report.modelPrediction.modelName),
      bullet("Human oversight required", "Yes"),
    );
  }

  children.push(heading("NLP extracted features", HeadingLevel.HEADING_2));
  for (const f of report.extractedFeatures) {
    children.push(bullet(f.label, `${f.value.toFixed(2)} (${f.source})`));
  }

  children.push(heading("Weighted evidence scores", HeadingLevel.HEADING_2));
  for (const w of report.weightedScores) {
    const sign = w.weightedContribution >= 0 ? "+" : "";
    children.push(
      bullet(
        w.category,
        `(weight ${w.weight.toFixed(2)}) score ${w.score.toFixed(2)} → ${sign}${w.weightedContribution.toFixed(2)}`,
      ),
    );
  }

  if (report.missingElements.length) {
    children.push(heading("Missing conviction elements", HeadingLevel.HEADING_2));
    for (const g of report.missingElements) {
      children.push(
        bullet(`[${g.severity.toUpperCase()}] ${g.element}`, g.detail),
      );
    }
  }

  if (report.legalCrossReferences.length) {
    children.push(
      heading("Trinidad & Tobago legal cross-references", HeadingLevel.HEADING_2),
    );
    for (const ref of report.legalCrossReferences) {
      children.push(
        heading(`${ref.citation} — ${ref.sectionRef}: ${ref.title}`, HeadingLevel.HEADING_3),
        bullet("Source", ref.sourceTitle),
        body(ref.summary),
        bullet("Relevance", ref.relevance),
      );
    }
  }

  children.push(heading("Documents analysed", HeadingLevel.HEADING_2));
  for (const d of report.documents) {
    children.push(
      bullet(
        d.filename,
        `${d.wordCount} words — ${d.detectedTypes.join(", ")}`,
      ),
    );
  }

  children.push(heading("Strengths", HeadingLevel.HEADING_2));
  for (const s of report.strengths) {
    children.push(bullet(s.title, `(${s.category}) ${s.detail}`));
  }

  children.push(heading("Weaknesses and gaps", HeadingLevel.HEADING_2));
  for (const w of report.weaknesses) {
    children.push(
      bullet(
        `[${w.severity.toUpperCase()}] ${w.title}`,
        `(${w.category}) ${w.detail}`,
      ),
    );
  }

  children.push(heading("Bulletproofing recommendations", HeadingLevel.HEADING_2));
  for (const r of report.recommendations) {
    children.push(
      numbered(
        `${r.priority}. ${r.action} — ${r.rationale} (Ref: ${r.legalAnchor})`,
      ),
    );
  }

  children.push(
    heading("Anticipated King's Counsel cross-examination", HeadingLevel.HEADING_2),
  );
  for (const [i, q] of report.crossExamination.entries()) {
    children.push(
      heading(`${i + 1}. ${q.theme}`, HeadingLevel.HEADING_3),
      bullet("Target", q.targetWitness),
      bullet("Question", q.question),
      bullet("Purpose", q.purpose),
      bullet("Follow-up", q.followUp),
    );
  }

  children.push(
    heading("Bias and fairness notice", HeadingLevel.HEADING_2),
    body(report.biasNotice),
    body(report.disclaimer),
  );

  const doc = new Document({
    sections: [{ children }],
  });

  return Packer.toBlob(doc);
}

export async function downloadReportAsDocx(
  report: AnalysisReport,
  filename: string,
): Promise<void> {
  const blob = await reportToDocxBlob(report);
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename.endsWith(".docx") ? filename : `${filename}.docx`;
  link.click();
  URL.revokeObjectURL(url);
}

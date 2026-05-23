export type ReadinessBand = "STRONG" | "DEVELOPING" | "AT_RISK";
export type Severity = "high" | "medium" | "low";

export interface DocumentSummary {
  filename: string;
  kind: string;
  wordCount: number;
  detectedTypes: string[];
}

export interface Finding {
  category: string;
  title: string;
  detail: string;
  severity: Severity;
  evidenceRefs: string[];
}

export interface Recommendation {
  priority: number;
  action: string;
  rationale: string;
  legalAnchor: string;
}

export interface CrossExamQuestion {
  theme: string;
  targetWitness: string;
  question: string;
  purpose: string;
  followUp: string;
}

export interface AnalysisReport {
  caseReference: string;
  documents: DocumentSummary[];
  strengths: Finding[];
  weaknesses: Finding[];
  recommendations: Recommendation[];
  crossExamination: CrossExamQuestion[];
  readinessBand: ReadinessBand;
  readinessScore: number;
  summary: string;
  disclaimer: string;
}

export interface EvidenceRule {
  id: string;
  category: string;
  strengthPatterns: RegExp[];
  weaknessPatterns: RegExp[];
  strengthTitle: string;
  strengthDetail: string;
  weaknessTitle: string;
  weaknessDetail: string;
  bulletproofAction: string;
  legalAnchor: string;
  kcTheme: string;
}

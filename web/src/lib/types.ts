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

export interface ExtractedFeature {
  name: string;
  value: number;
  label: string;
  source: "nlp" | "rule";
}

export interface WeightedScore {
  category: string;
  weight: number;
  score: number;
  weightedContribution: number;
  note: string;
}

export interface MissingElement {
  element: string;
  severity: Severity;
  detail: string;
}

export interface ModelPrediction {
  convictionProbability: number;
  confidenceLabel: string;
  modelName: string;
  humanOversightRequired: boolean;
}

export interface LegalCrossReference {
  citation: string;
  sectionRef: string;
  sourceTitle: string;
  title: string;
  summary: string;
  relevance: string;
}

export interface AnalysisReport {
  caseReference: string;
  documents: DocumentSummary[];
  strengths: Finding[];
  weaknesses: Finding[];
  recommendations: Recommendation[];
  crossExamination: CrossExamQuestion[];
  extractedFeatures: ExtractedFeature[];
  weightedScores: WeightedScore[];
  missingElements: MissingElement[];
  legalCrossReferences: LegalCrossReference[];
  modelPrediction: ModelPrediction | null;
  readinessBand: ReadinessBand;
  readinessScore: number;
  compositeScore: number;
  summary: string;
  biasNotice: string;
  disclaimer: string;
}

export interface FeatureVector {
  credibleEyewitnesses: number;
  identificationQuality: number;
  forensicDna: number;
  forensicFingerprint: number;
  weaponRecovered: number;
  confessionRecorded: number;
  cctvPresent: number;
  chainOfCustody: number;
  statementQuality: number;
  expertForensic: number;
  disclosureComplete: number;
  hearsayRisk: number;
  timeToArrestScore: number;
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

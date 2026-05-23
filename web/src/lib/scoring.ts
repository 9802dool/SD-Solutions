import type { FeatureVector, MissingElement, Severity, WeightedScore } from "./types";

export const BIAS_NOTICE =
  "Historical crime datasets may reflect systemic bias in policing and prosecution. " +
  "SDS models must be audited for fairness before operational use and must never " +
  "consider protected characteristics (race, religion, neighbourhood proxies, etc.). " +
  "Predictions are supportive analytics only — not legal judgments.";

const EVIDENCE_WEIGHTS: Record<string, [number, string]> = {
  forensicDna: [0.95, "DNA / genetic evidence"],
  forensicFingerprint: [0.85, "Fingerprint evidence"],
  confessionRecorded: [0.8, "Recorded confession (lawfully obtained)"],
  cctvPresent: [0.75, "CCTV / video corroboration"],
  weaponRecovered: [0.7, "Physical weapon link"],
  credibleEyewitnesses: [0.65, "Independent eyewitnesses"],
  identificationQuality: [0.6, "Identification procedure quality"],
  expertForensic: [0.6, "Expert / laboratory report"],
  chainOfCustody: [0.55, "Exhibit continuity"],
  statementQuality: [0.5, "Witness statement quality"],
  disclosureComplete: [0.45, "Disclosure completeness"],
  timeToArrestScore: [0.35, "Investigation timeliness"],
  hearsayRisk: [-0.5, "Hearsay exposure (penalty)"],
};

function normalize(key: keyof FeatureVector, value: number): number {
  if (key === "credibleEyewitnesses") return Math.min(1, value / 3);
  return Math.max(0, Math.min(1, value));
}

export function computeWeightedScores(vector: FeatureVector): WeightedScore[] {
  const scores: WeightedScore[] = [];

  for (const [key, [weight, label]] of Object.entries(EVIDENCE_WEIGHTS)) {
    const raw = vector[key as keyof FeatureVector];
    const normalized = key === "hearsayRisk" ? raw : normalize(key as keyof FeatureVector, raw);
    const contribution = weight * normalized;
    scores.push({
      category: label,
      weight,
      score: normalized,
      weightedContribution: contribution,
      note:
        key === "hearsayRisk"
          ? "Penalty applied when hearsay language appears."
          : `Weighted contribution: ${contribution.toFixed(2)}`,
    });
  }

  return scores.sort((a, b) => Math.abs(b.weightedContribution) - Math.abs(a.weightedContribution));
}

export function compositeScoreFromWeights(scores: WeightedScore[]): number {
  const totalWeight = scores.filter((s) => s.weight > 0).reduce((sum, s) => sum + s.weight, 0);
  if (!totalWeight) return 0;
  const raw = scores.reduce((sum, s) => sum + s.weightedContribution, 0);
  return Math.max(0, Math.min(100, Math.round((raw / totalWeight) * 100)));
}

export function detectMissingElements(vector: FeatureVector): MissingElement[] {
  const missing: MissingElement[] = [];
  const forensicOk =
    vector.forensicDna >= 1 || vector.forensicFingerprint >= 1 || vector.expertForensic >= 1;
  const witnessOk = vector.credibleEyewitnesses >= 1 || vector.identificationQuality >= 0.5;

  const checks: { ok: boolean; element: string; severity: Severity; detail: string }[] = [
    {
      ok: forensicOk,
      element: "Forensic link (DNA, fingerprint, or expert report)",
      severity: "high",
      detail: "No clear forensic or expert laboratory link detected in the file text.",
    },
    {
      ok: witnessOk,
      element: "Independent eyewitness or strong identification",
      severity: "high",
      detail: "No credible eyewitness or robust identification procedure referenced.",
    },
    {
      ok: vector.chainOfCustody >= 0.5,
      element: "Exhibit chain of custody",
      severity: "medium",
      detail: "Continuity of physical exhibits is not documented in the uploaded text.",
    },
    {
      ok: vector.statementQuality >= 0.5,
      element: "Lawful recorded statement",
      severity: "medium",
      detail: "No indication of a properly recorded and cautioned statement.",
    },
    {
      ok: vector.disclosureComplete >= 1,
      element: "Disclosure schedule",
      severity: "medium",
      detail: "Disclosure / unused-material review not evidenced in the bundle.",
    },
  ];

  for (const item of checks) {
    if (!item.ok) {
      missing.push({ element: item.element, severity: item.severity, detail: item.detail });
    }
  }
  return missing;
}

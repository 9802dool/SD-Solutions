import type { FeatureVector, ModelPrediction } from "./types";
import { vectorToList } from "./features";

const IMPORTANCES: Record<string, number> = {
  credible_eyewitnesses: 0.08187514955731037,
  identification_quality: 0.15823163436228765,
  forensic_dna: 0.010812993539124195,
  forensic_fingerprint: 0.020328917313841944,
  weapon_recovered: 0.01881098614766957,
  confession_recorded: 0.011306532663316585,
  cctv_present: 0.0320424498031282,
  chain_of_custody: 0.153174482320211,
  statement_quality: 0.1453138256216146,
  expert_forensic: 0.039948457112401844,
  disclosure_complete: 0.12791228871630883,
  hearsay_risk: 0.028056951423785597,
  time_to_arrest_score: 0.17218533141899978,
};

function confidenceLabel(probability: number): string {
  const pct = probability * 100;
  if (pct >= 75) return `${pct.toFixed(0)}% Strong`;
  if (pct >= 50) return `${pct.toFixed(0)}% Developing`;
  return `${pct.toFixed(0)}% At risk`;
}

function heuristicProbability(vector: FeatureVector): number {
  const weights: Record<keyof FeatureVector, number> = {
    forensicDna: 0.18,
    forensicFingerprint: 0.14,
    confessionRecorded: 0.12,
    cctvPresent: 0.1,
    credibleEyewitnesses: 0.08,
    identificationQuality: 0.08,
    weaponRecovered: 0.07,
    expertForensic: 0.07,
    chainOfCustody: 0.06,
    statementQuality: 0.05,
    disclosureComplete: 0.04,
    timeToArrestScore: 0.03,
    hearsayRisk: -0.12,
  };

  let z = -0.5;
  for (const [key, w] of Object.entries(weights)) {
    let val = vector[key as keyof FeatureVector];
    if (key === "credibleEyewitnesses") val = Math.min(1, val / 3);
    z += w * val;
  }
  const prob = 1 / (1 + Math.exp(-5 * z));
  return Math.max(0.05, Math.min(0.95, prob));
}

/** Importance-weighted score mirroring trained Random Forest signals. */
function importanceWeightedProbability(vector: FeatureVector): number {
  const values = vectorToList(vector);
  const keys = Object.keys(IMPORTANCES);
  let score = 0;
  let total = 0;
  keys.forEach((key, i) => {
    const imp = IMPORTANCES[key];
    let val = values[i];
    if (key === "credible_eyewitnesses") val = Math.min(1, val / 3);
    if (key === "hearsay_risk") {
      score -= imp * val;
    } else {
      score += imp * Math.max(0, Math.min(1, val));
    }
    total += imp;
  });
  return Math.max(0.05, Math.min(0.95, score / total));
}

export function predictConvictionStrength(vector: FeatureVector): ModelPrediction {
  const heuristic = heuristicProbability(vector);
  const rfProxy = importanceWeightedProbability(vector);
  const probability = (heuristic + rfProxy) / 2;

  return {
    convictionProbability: Math.round(probability * 1000) / 1000,
    confidenceLabel: confidenceLabel(probability),
    modelName: "random-forest-proxy-v1 (browser)",
    humanOversightRequired: true,
  };
}

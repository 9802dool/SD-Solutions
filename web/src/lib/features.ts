import type { ExtractedFeature, FeatureVector } from "./types";

function count(patterns: RegExp[], text: string): number {
  return patterns.filter((p) => p.test(text)).length;
}

function bool(patterns: RegExp[], text: string): number {
  return patterns.some((p) => p.test(text)) ? 1 : 0;
}

const p = (source: string) => new RegExp(source, "i");

export function extractFeatures(text: string): {
  vector: FeatureVector;
  details: ExtractedFeature[];
} {
  const lower = text.toLowerCase();
  const details: ExtractedFeature[] = [];

  const witnessHits = count(
    [
      p(String.raw`\b(independent witness|eyewitness|credible witness|corroborated witness)\b`),
      p(String.raw`\b(multiple witnesses|two witnesses|three witnesses)\b`),
    ],
    lower,
  );
  const credibleEyewitnesses = Math.min(3, witnessHits + (/\bwitness\b/i.test(lower) ? 1 : 0));
  details.push({
    name: "credibleEyewitnesses",
    value: credibleEyewitnesses,
    label: `${credibleEyewitnesses} eyewitness signal(s)`,
    source: "nlp",
  });

  const idGood = bool(
    [
      p(String.raw`\b(identification parade|line[- ]?up|CCTV (still|footage)|Turnbull)\b`),
      p(String.raw`\b(independent witness|multiple witnesses)\b`),
    ],
    lower,
  );
  const idBad = bool(
    [p(String.raw`\b(show[- ]?up|single photo|brief glimpse|poor lighting|one witness only)\b`)],
    lower,
  );
  const identificationQuality = Math.max(0, Math.min(1, idGood - 0.5 * idBad));
  details.push({
    name: "identificationQuality",
    value: identificationQuality,
    label: "Identification procedure quality (0–1)",
    source: "nlp",
  });

  const forensicDna = bool([p(String.raw`\b(DNA|genetic profile|STR profile)\b`)], lower);
  const forensicFingerprint = bool([p(String.raw`\b(fingerprint|latent print|AFIS)\b`)], lower);
  const weaponRecovered = bool(
    [p(String.raw`\b(firearm recovered|weapon seized|knife recovered|gun found)\b`)],
    lower,
  );
  const confessionRecorded = bool(
    [p(String.raw`\b(confession|admission|recorded interview|caution administered)\b`)],
    lower,
  );
  const cctvPresent = bool([p(String.raw`\b(CCTV|footage|DVR|video clip)\b`)], lower);

  const chainGood = bool(
    [p(String.raw`\b(chain of custody|sealed bag|custody log|property room)\b`)],
    lower,
  );
  const chainBad = bool([p(String.raw`\b(gap in custody|unsealed|broken seal|no continuity)\b`)], lower);
  const chainOfCustody = Math.max(0, Math.min(1, chainGood - 0.6 * chainBad));

  const stmtGood = bool(
    [p(String.raw`\b(recorded interview|signed statement|contemporaneous notes)\b`)],
    lower,
  );
  const stmtBad = bool([p(String.raw`\b(verbal only|unsigned|not recorded|no caution)\b`)], lower);
  const statementQuality = Math.max(0, Math.min(1, stmtGood - 0.6 * stmtBad));

  const expertForensic = bool(
    [p(String.raw`\b(expert report|forensic examiner|laboratory report|ISO 17025)\b`)],
    lower,
  );
  const disclosureComplete = bool(
    [p(String.raw`\b(disclosure schedule|unused material|prosecution bundle)\b`)],
    lower,
  );
  const hearsayRisk = bool(
    [p(String.raw`\b(hearsay|someone told me|rumour|second[- ]hand)\b`)],
    lower,
  );

  let timeToArrestScore = 0.5;
  if (/\b(within \d+ hours?|same day arrest)\b/i.test(lower)) timeToArrestScore = 0.9;
  else if (/\b(within \d+ days?)\b/i.test(lower)) timeToArrestScore = 0.7;
  if (/\b(months? later|years? later|delayed arrest)\b/i.test(lower)) timeToArrestScore = 0.2;

  const vector: FeatureVector = {
    credibleEyewitnesses,
    identificationQuality,
    forensicDna,
    forensicFingerprint,
    weaponRecovered,
    confessionRecorded,
    cctvPresent,
    chainOfCustody,
    statementQuality,
    expertForensic,
    disclosureComplete,
    hearsayRisk,
    timeToArrestScore,
  };

  for (const [name, value, label] of [
    ["forensicDna", forensicDna, "DNA / genetic evidence"],
    ["forensicFingerprint", forensicFingerprint, "Fingerprint evidence"],
    ["weaponRecovered", weaponRecovered, "Weapon recovered"],
    ["confessionRecorded", confessionRecorded, "Recorded confession / interview"],
    ["cctvPresent", cctvPresent, "CCTV / video evidence"],
    ["chainOfCustody", chainOfCustody, "Chain of custody integrity"],
    ["statementQuality", statementQuality, "Witness statement quality"],
    ["expertForensic", expertForensic, "Expert / lab report"],
    ["disclosureComplete", disclosureComplete, "Disclosure schedule present"],
    ["hearsayRisk", hearsayRisk, "Hearsay risk indicator"],
    ["timeToArrestScore", timeToArrestScore, "Timeliness of arrest (proxy)"],
  ] as const) {
    details.push({ name, value, label, source: "nlp" });
  }

  return { vector, details };
}

export function vectorToList(v: FeatureVector): number[] {
  return [
    v.credibleEyewitnesses,
    v.identificationQuality,
    v.forensicDna,
    v.forensicFingerprint,
    v.weaponRecovered,
    v.confessionRecorded,
    v.cctvPresent,
    v.chainOfCustody,
    v.statementQuality,
    v.expertForensic,
    v.disclosureComplete,
    v.hearsayRisk,
    v.timeToArrestScore,
  ];
}

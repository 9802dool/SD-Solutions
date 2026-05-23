import type { CrossExamQuestion, Finding, Severity } from "./types";

type QuestionTemplate = [string, string, string, string];

const KC_QUESTION_BANK: Record<string, QuestionTemplate[]> = {
  "Admissibility and fairness of statement": [
    [
      "Investigating officer",
      "Officer, before this statement was taken, what exact caution was administered—and where is that recorded?",
      "Tests whether caution and rights were properly given and documented.",
      "And if the recording equipment failed, why was the interview not paused until it was restored?",
    ],
  ],
  "Chain of custody": [
    [
      "Property officer / exhibits officer",
      "Exhibit {exhibit}, as you call it—who had custody between seizure and the property room, and where is each signature?",
      "Exposes gaps in physical continuity.",
      "If the seal was broken, who authorised that, and was the defence notified?",
    ],
  ],
  "Identification reliability": [
    [
      "Identifying witness",
      "You say you are sure—but you had only a brief glimpse in poor light, did you not?",
      "Classic Turnbull-style challenge on opportunity to observe.",
      "And you did not pick the accused out at a formal parade—you were shown a single photograph, were you not?",
    ],
  ],
  "Digital authentication": [
    [
      "Digital forensic examiner",
      "Where is the SHA-256 hash of the extracted data, and who verified it on receipt at the lab?",
      "Tests whether digital evidence meets authentication standards.",
      "If all you have is a screenshot, how do you exclude the possibility of editing before capture?",
    ],
  ],
  "Hearsay and documentary foundation": [
    [
      "Document witness / records keeper",
      "Who created this document, and can that person attend to prove its contents?",
      "Challenges hearsay where maker is not called.",
      "This is a photocopy—where is the original, or the certificate permitting its use?",
    ],
  ],
  "Credibility and consistency": [
    [
      "Complainant / witness",
      "In your first account you said {detail_a}; today you say {detail_b}—which is true?",
      "Prior inconsistent statement attack.",
      "Were you trying to help the police, rather than tell the whole truth?",
    ],
  ],
  "Disclosure failure": [
    [
      "Prosecutor / disclosure officer",
      "When did you first become aware of {material}, and why was it not on the initial disclosure schedule?",
      "Anticipates abuse-of-process and fair-trial challenges.",
      "Was this material capable of undermining the prosecution case or assisting the accused?",
    ],
  ],
  "Expert qualifications and methodology": [
    [
      "Forensic expert",
      "What accredited standard governs your method, and when was your equipment last calibrated?",
      "Challenges expert foundation under cross-examination.",
      "If contamination occurred at collection, would your results be meaningless?",
    ],
  ],
};

const CATEGORY_THEME: Record<string, string> = {
  "Witness statements": "Admissibility and fairness of statement",
  "Exhibits and continuity": "Chain of custody",
  "Identification evidence": "Identification reliability",
  "Digital / cyber evidence": "Digital authentication",
  "Documentary / hearsay": "Hearsay and documentary foundation",
  "Corroboration and consistency": "Credibility and consistency",
  "Disclosure and unused material": "Disclosure failure",
  "Expert / forensic evidence": "Expert qualifications and methodology",
};

function formatTemplate(
  template: string,
  vars: Record<string, string>,
): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => vars[key] ?? "");
}

export function weaknessToSeverity(title: string): Severity {
  const highMarkers = ["disclosure", "chain", "identification", "hearsay", "digital"];
  const lowered = title.toLowerCase();
  return highMarkers.some((m) => lowered.includes(m)) ? "high" : "medium";
}

export function generateCrossExamination(
  weaknesses: Finding[],
  vars: Record<string, string> = {
    exhibit: "A",
    detail_a: "the incident occurred at 9 p.m.",
    detail_b: "10 p.m.",
    material: "the CCTV clip showing another person at the scene",
  },
): CrossExamQuestion[] {
  const questions: CrossExamQuestion[] = [];
  const seenThemes = new Set<string>();

  for (const weakness of weaknesses) {
    const theme = CATEGORY_THEME[weakness.category] ?? weakness.category;
    if (seenThemes.has(theme)) continue;
    const bank = KC_QUESTION_BANK[theme];
    if (!bank) continue;

    seenThemes.add(theme);
    const [targetWitness, question, purpose, followUp] = bank[0];
    questions.push({
      theme,
      targetWitness,
      question: formatTemplate(question, vars),
      purpose,
      followUp: formatTemplate(followUp, vars),
    });
  }

  if (questions.length === 0) {
    questions.push({
      theme: "General prosecution testing",
      targetWitness: "Investigating officer",
      question:
        "Officer, having reviewed the file, what single piece of evidence, if disbelieved, would collapse your case?",
      purpose:
        "Forces identification of the critical dependency — a standard senior-counsel stress test.",
      followUp: "And what have you done to independently verify that piece of evidence?",
    });
  }

  return questions;
}

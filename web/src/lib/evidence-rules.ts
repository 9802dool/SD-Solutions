import type { EvidenceRule } from "./types";

const p = (source: string, flags = "i") => new RegExp(source, flags);

export const EVIDENCE_RULES: EvidenceRule[] = [
  {
    id: "statement_record",
    category: "Witness statements",
    strengthPatterns: [
      p(String.raw`\b(recorded interview|audio[- ]recorded|video[- ]recorded|judges rules)\b`),
      p(String.raw`\b(contemporaneous notes|notebook entry|signed statement)\b`),
      p(String.raw`\b(right to silence|legal advice|caution administered)\b`),
    ],
    weaknessPatterns: [
      p(String.raw`\b(verbal only|no recording|not recorded|unsigned)\b`),
      p(String.raw`\b(no caution|failed to caution|without caution)\b`),
      p(String.raw`\b(translation|interpreter).{0,40}(not|without|no)\b`),
    ],
    strengthTitle: "Statement process appears documented",
    strengthDetail:
      "Materials reference recording, caution, or contemporaneous notes — supports admissibility review.",
    weaknessTitle: "Statement process may be challengeable",
    weaknessDetail:
      "Text suggests gaps in recording, caution, or signed statement formalities.",
    bulletproofAction:
      "Obtain complete recording, caution sheet, and signed statement; confirm interpreter certificate if used.",
    legalAnchor: "Evidence Act; Judges Rules; Police and Bail Act (statement procedures)",
    kcTheme: "Admissibility and fairness of statement",
  },
  {
    id: "chain_of_custody",
    category: "Exhibits and continuity",
    strengthPatterns: [
      p(String.raw`\b(chain of custody|continuity|sealed bag|property room|exhibit label)\b`),
      p(String.raw`\b(signed receipt|handover|custody log|tamper[- ]evident)\b`),
    ],
    weaknessPatterns: [
      p(String.raw`\b(unsealed|broken seal|missing exhibit|lost exhibit)\b`),
      p(String.raw`\b(no continuity|gap in custody|unaccounted)\b`),
      p(String.raw`\b(photograph(ed)? only.{0,30}(no physical|without seizing))\b`),
    ],
    strengthTitle: "Exhibit continuity appears tracked",
    strengthDetail:
      "Chain-of-custody or sealed-exhibit references support integrity of physical evidence.",
    weaknessTitle: "Exhibit continuity may be incomplete",
    weaknessDetail: "Possible gaps in sealing, handover logs, or exhibit tracking.",
    bulletproofAction:
      "Reconstruct continuity with signed movements; photograph seals; obtain property-room register entries.",
    legalAnchor: "Evidence Act — proof of integrity of real evidence",
    kcTheme: "Chain of custody",
  },
  {
    id: "identification",
    category: "Identification evidence",
    strengthPatterns: [
      p(String.raw`\b(line[- ]?up|identification parade|photo spread|dock identification)\b`),
      p(String.raw`\b(Turnbull|special warning|recognition|CCTV still)\b`),
      p(String.raw`\b(independent witness|multiple witnesses)\b`),
    ],
    weaknessPatterns: [
      p(String.raw`\b(show[- ]?up|single photo|informal identification)\b`),
      p(String.raw`\b(brief glimpse|poor lighting|mask(ed)?|hoodie)\b`),
      p(String.raw`\b(no parade|failed to hold parade|one witness only)\b`),
    ],
    strengthTitle: "Identification procedure referenced",
    strengthDetail:
      "Materials mention parade, CCTV, or corroborated identification — useful for Turnbull-style review.",
    weaknessTitle: "Identification evidence may be fragile",
    weaknessDetail:
      "Informal ID, poor viewing conditions, or single-witness identification increases challenge risk.",
    bulletproofAction:
      "Document viewing conditions; obtain CCTV continuity; consider formal ID procedure where feasible.",
    legalAnchor: "Evidence Act; common-law Turnbull principles (identification warnings)",
    kcTheme: "Identification reliability",
  },
  {
    id: "digital_evidence",
    category: "Digital / cyber evidence",
    strengthPatterns: [
      p(String.raw`\b(hash (value|sum)|MD5|SHA-?256|forensic image|write[- ]blocker)\b`),
      p(String.raw`\b(metadata preserved|extraction certificate|chain of digital custody)\b`),
      p(String.raw`\b(Cybercrime|digital evidence unit|forensic examiner)\b`),
    ],
    weaknessPatterns: [
      p(String.raw`\b(screenshot only|printout only|no hash|altered metadata)\b`),
      p(String.raw`\b(unverified device|shared password|unsecured phone)\b`),
      p(String.raw`\b(WhatsApp export).{0,40}(without|no).{0,20}(certificate|hash)\b`),
    ],
    strengthTitle: "Digital integrity controls referenced",
    strengthDetail:
      "Hash values, forensic imaging, or cyber unit involvement support integrity arguments.",
    weaknessTitle: "Digital evidence may lack forensic integrity",
    weaknessDetail:
      "Screenshots/printouts without hash or forensic capture are vulnerable to tampering arguments.",
    bulletproofAction:
      "Obtain forensic image, hash verification, examiner statement, and device seizure continuity.",
    legalAnchor: "Computer Misuse Act; Evidence Act — authentication of electronic records",
    kcTheme: "Digital authentication",
  },
  {
    id: "hearsay_and_docs",
    category: "Documentary / hearsay",
    strengthPatterns: [
      p(String.raw`\b(business record|original document|certified copy|public record)\b`),
      p(String.raw`\b(maker available|author identified|witness to creation)\b`),
    ],
    weaknessPatterns: [
      p(String.raw`\b(hearsay|rumour|second[- ]hand|someone told me)\b`),
      p(String.raw`\b(photocopy|uncertified copy|anonymous source)\b`),
      p(String.raw`\b(no author|unknown origin|unverified document)\b`),
    ],
    strengthTitle: "Documentary foundation appears addressed",
    strengthDetail:
      "References to originals, business records, or identifiable authors support hearsay exceptions.",
    weaknessTitle: "Hearsay or weak documentary foundation",
    weaknessDetail:
      "Second-hand accounts or uncertified copies may require a hearsay gateway or live witness.",
    bulletproofAction:
      "Identify document maker; obtain certificate or live evidence; replace copies with authenticated originals.",
    legalAnchor: "Evidence Act — hearsay and documentary exceptions",
    kcTheme: "Hearsay and documentary foundation",
  },
  {
    id: "corroboration",
    category: "Corroboration and consistency",
    strengthPatterns: [
      p(String.raw`\b(corroborated|independent source|CCTV confirms|telephone records)\b`),
      p(String.raw`\b(consistent with|supports account|multiple exhibits)\b`),
    ],
    weaknessPatterns: [
      p(String.raw`\b(sole witness|uncorroborated|single source)\b`),
      p(String.raw`\b(inconsistent|contradicts|changed story|prior statement differs)\b`),
    ],
    strengthTitle: "Corroboration signals present",
    strengthDetail:
      "Independent sources or consistency references strengthen the prosecution narrative.",
    weaknessTitle: "Corroboration or consistency concerns",
    weaknessDetail:
      "Single-witness cases or internal inconsistencies invite robust cross-examination.",
    bulletproofAction:
      "Seek independent corroboration (CCTV, billing, GPS, third-party witnesses); reconcile inconsistencies early.",
    legalAnchor: "Evidence Act; general principles on proof beyond reasonable doubt",
    kcTheme: "Credibility and consistency",
  },
  {
    id: "disclosure",
    category: "Disclosure and unused material",
    strengthPatterns: [
      p(String.raw`\b(disclosure schedule|unused material|MG6|prosecution bundle)\b`),
      p(String.raw`\b(exculpatory|immaterial|reviewed by prosecutor)\b`),
    ],
    weaknessPatterns: [
      p(String.raw`\b(not disclosed|late disclosure|missing pages|withheld)\b`),
      p(String.raw`\b(unreviewed material|unknown witness|undocumented interview)\b`),
    ],
    strengthTitle: "Disclosure process referenced",
    strengthDetail:
      "Mention of schedules or unused-material review supports fair-trial obligations.",
    weaknessTitle: "Disclosure risk indicators",
    weaknessDetail:
      "Late or incomplete disclosure can collapse trials and invite abuse-of-process applications.",
    bulletproofAction:
      "Complete unused-material review; update disclosure schedule; document all witness contacts.",
    legalAnchor: "Constitution fair trial; criminal procedure disclosure duties",
    kcTheme: "Disclosure failure",
  },
  {
    id: "expert_evidence",
    category: "Expert / forensic evidence",
    strengthPatterns: [
      p(String.raw`\b(expert report|qualifications|accredited lab|ISO 17025)\b`),
      p(String.raw`\b(methodology|peer review|control sample|calibration)\b`),
    ],
    weaknessPatterns: [
      p(String.raw`\b(unqualified|informal opinion|no report|verbal opinion)\b`),
      p(String.raw`\b(no calibration|contaminated sample|broken procedure)\b`),
    ],
    strengthTitle: "Expert foundation referenced",
    strengthDetail:
      "Formal expert report or accredited laboratory references support Daubert-style scrutiny.",
    weaknessTitle: "Expert evidence may lack foundation",
    weaknessDetail:
      "Informal opinions or procedural gaps in forensic handling are common attack lines.",
    bulletproofAction:
      "Obtain full expert statement, CV, methodology, lab accreditation, and sample continuity.",
    legalAnchor: "Evidence Act — opinion evidence and expert witnesses",
    kcTheme: "Expert qualifications and methodology",
  },
];

export function countPatternMatches(text: string, patterns: RegExp[]): string[] {
  const hits: string[] = [];
  for (const pattern of patterns) {
    if (pattern.test(text)) hits.push(pattern.source);
  }
  return hits;
}

export function detectDocumentTypes(text: string): string[] {
  const mapping: Record<string, RegExp> = {
    "Witness statement": p(String.raw`\b(statement of|i (?:state|saw|observed)|deponent|affidavit)\b`),
    "Scene notes / notebook": p(String.raw`\b(notebook|scene visit|occurrence book|OB entry)\b`),
    "Charge / indictment": p(String.raw`\b(charge|indictment|information laid|count \d)\b`),
    "Exhibit list": p(String.raw`\b(exhibit [A-Z0-9]+|property register|seized items)\b`),
    "Forensic report": p(String.raw`\b(laboratory report|forensic|ballistics|DNA|toxicology)\b`),
    "CCTV / video": p(String.raw`\b(CCTV|footage|camera|DVR|video clip)\b`),
    "Medical report": p(String.raw`\b(medical report|post mortem|PM report|injury report|doctor)\b`),
    "Disclosure schedule": p(String.raw`\b(disclosure|unused material|schedule of evidence)\b`),
  };

  return Object.entries(mapping)
    .filter(([, pattern]) => pattern.test(text))
    .map(([label]) => label);
}

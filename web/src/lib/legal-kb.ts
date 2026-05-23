import type { LegalCrossReference } from "./types";

export interface LegalSectionRecord {
  id: number;
  citation: string;
  sourceTitle: string;
  sectionRef: string;
  title: string;
  summary: string;
  keywords: string;
  evidenceTags: string[];
  fullText?: string | null;
}

export interface LegalKnowledgeBase {
  jurisdiction: string;
  sources: Array<{
    id: number;
    title: string;
    sourceType: string;
    citation: string;
    jurisdiction: string;
    officialUrl?: string | null;
    summary?: string | null;
  }>;
  sections: LegalSectionRecord[];
}

let cachedKb: LegalKnowledgeBase | null = null;

export async function loadLegalKb(): Promise<LegalKnowledgeBase> {
  if (cachedKb) return cachedKb;
  const res = await fetch("/legal/kb.json");
  if (!res.ok) throw new Error("Legal knowledge base not found. Run: python -m legal_kb init");
  cachedKb = (await res.json()) as LegalKnowledgeBase;
  return cachedKb;
}

const CATEGORY_TAG_MAP: Record<string, string[]> = {
  "Witness statements": ["Witness statements"],
  "Exhibits and continuity": ["Exhibits and continuity"],
  "Identification evidence": ["Identification evidence", "Corroboration and consistency"],
  "Digital / cyber evidence": ["Digital / cyber evidence"],
  "Documentary / hearsay": ["Documentary / hearsay"],
  "Corroboration and consistency": ["Corroboration and consistency", "Identification evidence"],
  "Disclosure and unused material": ["Disclosure and unused material"],
  "Expert / forensic evidence": ["Expert / forensic evidence"],
};

const TEXT_TRIGGERS: Array<[RegExp, string[]]> = [
  [/\b(hearsay|someone told me|rumour)\b/i, ["Documentary / hearsay"]],
  [/\b(DNA|fingerprint|forensic|laboratory)\b/i, ["Expert / forensic evidence", "Digital / cyber evidence"]],
  [/\b(CCTV|footage|video)\b/i, ["Identification evidence", "Digital / cyber evidence"]],
  [/\b(disclosure|unused material)\b/i, ["Disclosure and unused material"]],
  [/\b(caution|statement|recorded interview)\b/i, ["Witness statements"]],
  [/\b(exhibit|chain of custody|sealed)\b/i, ["Exhibits and continuity"]],
];

export function crossReferenceCase(
  kb: LegalKnowledgeBase,
  combinedText: string,
  weaknessCategories: string[],
  missingElements: string[],
): LegalCrossReference[] {
  const tags = new Set<string>();

  for (const cat of weaknessCategories) {
    for (const t of CATEGORY_TAG_MAP[cat] ?? [cat]) tags.add(t);
  }
  for (const [pattern, patternTags] of TEXT_TRIGGERS) {
    if (pattern.test(combinedText)) patternTags.forEach((t) => tags.add(t));
  }
  for (const element of missingElements) {
    const lower = element.toLowerCase();
    if (lower.includes("forensic") || lower.includes("dna")) {
      ["Expert / forensic evidence", "Digital / cyber evidence"].forEach((t) => tags.add(t));
    }
    if (lower.includes("eyewitness") || lower.includes("identification")) {
      ["Identification evidence", "Corroboration and consistency"].forEach((t) => tags.add(t));
    }
    if (lower.includes("custody") || lower.includes("exhibit")) tags.add("Exhibits and continuity");
    if (lower.includes("statement")) tags.add("Witness statements");
    if (lower.includes("disclosure")) tags.add("Disclosure and unused material");
  }

  const tagSet = [...tags].map((t) => t.toLowerCase());
  const matched = kb.sections.filter((sec) =>
    sec.evidenceTags.some((t) => tagSet.includes(t.toLowerCase())),
  );

  for (const term of ["hearsay", "DNA", "CCTV", "disclosure", "caution", "exhibit", "confession"]) {
    if (new RegExp(`\\b${term}\\b`, "i").test(combinedText)) {
      kb.sections
        .filter(
          (s) =>
            s.summary.toLowerCase().includes(term.toLowerCase()) ||
            s.keywords.toLowerCase().includes(term.toLowerCase()),
        )
        .slice(0, 2)
        .forEach((s) => matched.push(s));
    }
  }

  const seen = new Set<number>();
  const unique: LegalCrossReference[] = [];
  for (const sec of matched) {
    if (seen.has(sec.id)) continue;
    seen.add(sec.id);
    unique.push({
      citation: sec.citation,
      sectionRef: sec.sectionRef,
      sourceTitle: sec.sourceTitle,
      title: sec.title,
      summary: sec.summary,
      relevance: `Cross-referenced to: ${sec.evidenceTags.join(", ") || "general"}`,
    });
    if (unique.length >= 12) break;
  }
  return unique;
}

export function searchLegalKb(kb: LegalKnowledgeBase, query: string): LegalSectionRecord[] {
  const q = query.toLowerCase();
  return kb.sections.filter(
    (s) =>
      s.title.toLowerCase().includes(q) ||
      s.summary.toLowerCase().includes(q) ||
      s.keywords.toLowerCase().includes(q) ||
      s.citation.toLowerCase().includes(q),
  );
}

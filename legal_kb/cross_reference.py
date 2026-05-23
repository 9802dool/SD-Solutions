from __future__ import annotations

import re

from .db import LegalDatabase, LegalSection

CATEGORY_TAG_MAP: dict[str, list[str]] = {
    "Witness statements": ["Witness statements"],
    "Exhibits and continuity": ["Exhibits and continuity"],
    "Identification evidence": ["Identification evidence", "Corroboration and consistency"],
    "Digital / cyber evidence": ["Digital / cyber evidence"],
    "Documentary / hearsay": ["Documentary / hearsay"],
    "Corroboration and consistency": ["Corroboration and consistency", "Identification evidence"],
    "Disclosure and unused material": ["Disclosure and unused material"],
    "Expert / forensic evidence": ["Expert / forensic evidence"],
}

TEXT_TRIGGER_MAP: list[tuple[str, list[str]]] = [
    (r"\b(hearsay|someone told me|rumour)\b", ["Documentary / hearsay"]),
    (r"\b(DNA|fingerprint|forensic|laboratory)\b", ["Expert / forensic evidence", "Digital / cyber evidence"]),
    (r"\b(CCTV|footage|video)\b", ["Identification evidence", "Digital / cyber evidence"]),
    (r"\b(disclosure|unused material)\b", ["Disclosure and unused material"]),
    (r"\b(caution|statement|recorded interview)\b", ["Witness statements"]),
    (r"\b(exhibit|chain of custody|sealed)\b", ["Exhibits and continuity"]),
]


def cross_reference_case(
    *,
    combined_text: str,
    weakness_categories: list[str],
    missing_elements: list[str],
    db: LegalDatabase | None = None,
) -> list[LegalSection]:
    db = db or LegalDatabase()
    tags: set[str] = set()

    for category in weakness_categories:
        tags.update(CATEGORY_TAG_MAP.get(category, [category]))

    for pattern, pattern_tags in TEXT_TRIGGER_MAP:
        if re.search(pattern, combined_text, re.I):
            tags.update(pattern_tags)

    for element in missing_elements:
        lower = element.lower()
        if "forensic" in lower or "dna" in lower:
            tags.update(["Expert / forensic evidence", "Digital / cyber evidence"])
        if "eyewitness" in lower or "identification" in lower:
            tags.update(["Identification evidence", "Corroboration and consistency"])
        if "custody" in lower or "exhibit" in lower:
            tags.add("Exhibits and continuity")
        if "statement" in lower:
            tags.add("Witness statements")
        if "disclosure" in lower:
            tags.add("Disclosure and unused material")

    sections = db.sections_by_tags(sorted(tags))

    # Keyword search on distinctive terms in the case file
    for term in ("hearsay", "DNA", "CCTV", "disclosure", "caution", "exhibit", "confession"):
        if re.search(rf"\b{term}\b", combined_text, re.I):
            sections.extend(db.search(term, limit=3))

    # Deduplicate by section id preserving order
    seen: set[int] = set()
    unique: list[LegalSection] = []
    for sec in sections:
        if sec.id not in seen:
            seen.add(sec.id)
            unique.append(sec)
    return unique[:12]

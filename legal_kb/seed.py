"""Seed Trinidad and Tobago legal knowledge base with summary sections for SDS cross-reference."""

from __future__ import annotations

from .db import LegalDatabase

# Summaries for cross-reference — not full statute text. Verify against official sources.


def seed_tt_legal_kb(db: LegalDatabase | None = None) -> None:
    db = db or LegalDatabase()

    sources = [
        (
            "Evidence Act",
            "act",
            "Chap 7:02",
            "https://www.ttlawcourts.org/",
            "Governs admissibility, hearsay, documentary and opinion evidence in T&T proceedings.",
        ),
        (
            "Constitution of Trinidad and Tobago",
            "constitution",
            "Constitution 1976",
            "https://www.ttparliament.org/",
            "Fundamental rights including fair hearing and protection from arbitrary treatment.",
        ),
        (
            "Police Service Act",
            "act",
            "Chap 15:01",
            "https://www.ttps.gov.tt/",
            "Mandate, discipline, and organisational lawfulness of the TTPS.",
        ),
        (
            "Criminal Procedure",
            "act",
            "Criminal Procedure Chap (in force provisions)",
            None,
            "Procedure for prosecution, disclosure, and trial conduct.",
        ),
        (
            "Computer Misuse Act",
            "act",
            "Chap 11:17",
            None,
            "Integrity of computer systems; lawful handling of digital evidence.",
        ),
        (
            "Data Protection Act",
            "act",
            "Act 2011 (partially proclaimed)",
            None,
            "Privacy and lawful processing of personal data by public bodies.",
        ),
        (
            "Judges Rules / Statement Guidance",
            "guidance",
            "Judges Rules (Commonwealth practice)",
            None,
            "Fair treatment of persons when statements are taken for use in criminal proceedings.",
        ),
    ]

    for title, stype, citation, url, summary in sources:
        db.add_source(
            title=title,
            source_type=stype,
            citation=citation,
            official_url=url,
            summary=summary,
        )

    sections = [
        (
            "Chap 7:02",
            "s5-hearsay",
            "Hearsay rule and exceptions",
            "Hearsay is generally excluded unless brought within a statutory or common-law exception. "
            "Prosecution should identify the exception and call the maker where required.",
            "hearsay, second-hand, rumour, document maker",
            "Documentary / hearsay, Corroboration and consistency",
        ),
        (
            "Chap 7:02",
            "s-real-evidence",
            "Real evidence and identification",
            "Physical exhibits must be identifiable and continuity must be provable. "
            "Identification evidence is scrutinised where witness observation conditions are poor.",
            "exhibit, identification, parade, Turnbull, CCTV",
            "Identification evidence, Exhibits and continuity",
        ),
        (
            "Chap 7:02",
            "s-documentary",
            "Documentary evidence",
            "Documents require proof of authenticity. Copies may need certification or "
            "a witness to prove the original or business-records foundation.",
            "original document, certified copy, business record, photocopy",
            "Documentary / hearsay",
        ),
        (
            "Chap 7:02",
            "s-opinion",
            "Opinion and expert evidence",
            "Expert opinion requires proof of qualifications, methodology, and reliable procedure. "
            "Informal opinions without report are vulnerable on cross-examination.",
            "expert report, forensic, laboratory, methodology, calibration",
            "Expert / forensic evidence",
        ),
        (
            "Chap 7:02",
            "s-electronic",
            "Electronic records",
            "Electronic records must be authenticated. Hash values, forensic imaging, and "
            "examiner evidence support integrity arguments for digital exhibits.",
            "hash, forensic image, WhatsApp, digital, metadata",
            "Digital / cyber evidence",
        ),
        (
            "Constitution 1976",
            "s4-fair-hearing",
            "Fair hearing",
            "Accused persons are entitled to a fair hearing. Late disclosure or concealment of "
            "unused material may breach fair-trial obligations.",
            "disclosure, unused material, fair trial, abuse of process",
            "Disclosure and unused material",
        ),
        (
            "Chap 15:01",
            "police-powers",
            "Police powers and lawful process",
            "TTPS powers must be exercised lawfully. Statements and seizures must follow "
            "established procedure and internal authorisation policies.",
            "caution, arrest, seizure, statement, notebook",
            "Witness statements, Exhibits and continuity",
        ),
        (
            "Criminal Procedure Chap (in force provisions)",
            "disclosure",
            "Prosecution disclosure",
            "Prosecution must disclose material relevant to the defence. Schedules should be "
            "kept current; failure risks stay or abuse-of-process applications.",
            "disclosure schedule, MG6, unused material, withheld",
            "Disclosure and unused material",
        ),
        (
            "Chap 11:17",
            "digital-seizure",
            "Computer Misuse and digital seizure",
            "Digital devices must be lawfully seized and forensically handled. "
            "Screenshots alone may not establish integrity without examiner evidence.",
            "device seizure, forensic, hash, cybercrime, screenshot",
            "Digital / cyber evidence",
        ),
        (
            "Act 2011 (partially proclaimed)",
            "data-processing",
            "Data protection in investigations",
            "Personal data in case files must be processed lawfully with access controls and "
            "retention limits appropriate to public-sector investigations.",
            "PII, personal data, retention, access log",
            "Disclosure and unused material, Witness statements",
        ),
        (
            "Judges Rules (Commonwealth practice)",
            "statement-fairness",
            "Fairness when taking statements",
            "Statements should be taken fairly with appropriate cautions and, where practicable, "
            "contemporaneous recording. Interpreter use must be documented.",
            "caution, recorded interview, interpreter, unsigned, verbal only",
            "Witness statements",
        ),
        (
            "Chap 7:02",
            "s-corroboration",
            "Corroboration and proof",
            "Prosecution must prove the case beyond reasonable doubt. Uncorroborated single-witness "
            "cases require careful assessment of consistency and independent support.",
            "sole witness, uncorroborated, consistent, CCTV confirms",
            "Corroboration and consistency, Identification evidence",
        ),
    ]

    for citation, ref, title, summary, keywords, tags in sections:
        db.add_section(
            citation=citation,
            section_ref=ref,
            title=title,
            summary=summary,
            keywords=keywords,
            evidence_tags=tags,
        )

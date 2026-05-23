from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceRule:
    id: str
    category: str
    strength_patterns: tuple[str, ...]
    weakness_patterns: tuple[str, ...]
    strength_title: str
    strength_detail: str
    weakness_title: str
    weakness_detail: str
    bulletproof_action: str
    legal_anchor: str
    kc_theme: str


# TT-oriented checklist themes mapped to Evidence Act / criminal procedure concepts.
# Patterns look for documentary signals — not proof of legal compliance.
EVIDENCE_RULES: tuple[EvidenceRule, ...] = (
    EvidenceRule(
        id="statement_record",
        category="Witness statements",
        strength_patterns=(
            r"\b(recorded interview|audio[- ]recorded|video[- ]recorded|judges rules)\b",
            r"\b(contemporaneous notes|notebook entry|signed statement)\b",
            r"\b(right to silence|legal advice|caution administered)\b",
        ),
        weakness_patterns=(
            r"\b(verbal only|no recording|not recorded|unsigned)\b",
            r"\b(no caution|failed to caution|without caution)\b",
            r"\b(translation|interpreter).{0,40}(not|without|no)\b",
        ),
        strength_title="Statement process appears documented",
        strength_detail="Materials reference recording, caution, or contemporaneous notes — supports admissibility review.",
        weakness_title="Statement process may be challengeable",
        weakness_detail="Text suggests gaps in recording, caution, or signed statement formalities.",
        bulletproof_action="Obtain complete recording, caution sheet, and signed statement; confirm interpreter certificate if used.",
        legal_anchor="Evidence Act; Judges Rules; Police and Bail Act (statement procedures)",
        kc_theme="Admissibility and fairness of statement",
    ),
    EvidenceRule(
        id="chain_of_custody",
        category="Exhibits and continuity",
        strength_patterns=(
            r"\b(chain of custody|continuity|sealed bag|property room|exhibit label)\b",
            r"\b(signed receipt|handover|custody log|tamper[- ]evident)\b",
        ),
        weakness_patterns=(
            r"\b(unsealed|broken seal|missing exhibit|lost exhibit)\b",
            r"\b(no continuity|gap in custody|unaccounted)\b",
            r"\b(photograph(ed)? only.{0,30}(no physical|without seizing))\b",
        ),
        strength_title="Exhibit continuity appears tracked",
        strength_detail="Chain-of-custody or sealed-exhibit references support integrity of physical evidence.",
        weakness_title="Exhibit continuity may be incomplete",
        weakness_detail="Possible gaps in sealing, handover logs, or exhibit tracking.",
        bulletproof_action="Reconstruct continuity with signed movements; photograph seals; obtain property-room register entries.",
        legal_anchor="Evidence Act — proof of integrity of real evidence",
        kc_theme="Chain of custody",
    ),
    EvidenceRule(
        id="identification",
        category="Identification evidence",
        strength_patterns=(
            r"\b(line[- ]?up|identification parade|photo spread|dock identification)\b",
            r"\b(Turnbull|special warning|recognition|CCTV still)\b",
            r"\b(independent witness|multiple witnesses)\b",
        ),
        weakness_patterns=(
            r"\b(show[- ]?up|single photo|informal identification)\b",
            r"\b(brief glimpse|poor lighting|mask(ed)?|hoodie)\b",
            r"\b(no parade|failed to hold parade|one witness only)\b",
        ),
        strength_title="Identification procedure referenced",
        strength_detail="Materials mention parade, CCTV, or corroborated identification — useful for Turnbull-style review.",
        weakness_title="Identification evidence may be fragile",
        weakness_detail="Informal ID, poor viewing conditions, or single-witness identification increases challenge risk.",
        bulletproof_action="Document viewing conditions; obtain CCTV continuity; consider formal ID procedure where feasible.",
        legal_anchor="Evidence Act; common-law Turnbull principles (identification warnings)",
        kc_theme="Identification reliability",
    ),
    EvidenceRule(
        id="digital_evidence",
        category="Digital / cyber evidence",
        strength_patterns=(
            r"\b(hash (value|sum)|MD5|SHA-?256|forensic image|write[- ]blocker)\b",
            r"\b(metadata preserved|extraction certificate|chain of digital custody)\b",
            r"\b(Cybercrime|digital evidence unit|forensic examiner)\b",
        ),
        weakness_patterns=(
            r"\b(screenshot only|printout only|no hash|altered metadata)\b",
            r"\b(unverified device|shared password|unsecured phone)\b",
            r"\b(WhatsApp export).{0,40}(without|no).{0,20}(certificate|hash)\b",
        ),
        strength_title="Digital integrity controls referenced",
        strength_detail="Hash values, forensic imaging, or cyber unit involvement support integrity arguments.",
        weakness_title="Digital evidence may lack forensic integrity",
        weakness_detail="Screenshots/printouts without hash or forensic capture are vulnerable to tampering arguments.",
        bulletproof_action="Obtain forensic image, hash verification, examiner statement, and device seizure continuity.",
        legal_anchor="Computer Misuse Act; Evidence Act — authentication of electronic records",
        kc_theme="Digital authentication",
    ),
    EvidenceRule(
        id="hearsay_and_docs",
        category="Documentary / hearsay",
        strength_patterns=(
            r"\b(business record|original document|certified copy|public record)\b",
            r"\b(maker available|author identified|witness to creation)\b",
        ),
        weakness_patterns=(
            r"\b(hearsay|rumour|second[- ]hand|someone told me)\b",
            r"\b(photocopy|uncertified copy|anonymous source)\b",
            r"\b(no author|unknown origin|unverified document)\b",
        ),
        strength_title="Documentary foundation appears addressed",
        strength_detail="References to originals, business records, or identifiable authors support hearsay exceptions.",
        weakness_title="Hearsay or weak documentary foundation",
        weakness_detail="Second-hand accounts or uncertified copies may require a hearsay gateway or live witness.",
        bulletproof_action="Identify document maker; obtain certificate or live evidence; replace copies with authenticated originals.",
        legal_anchor="Evidence Act — hearsay and documentary exceptions",
        kc_theme="Hearsay and documentary foundation",
    ),
    EvidenceRule(
        id="corroboration",
        category="Corroboration and consistency",
        strength_patterns=(
            r"\b(corroborated|independent source|CCTV confirms|telephone records)\b",
            r"\b(consistent with|supports account|multiple exhibits)\b",
        ),
        weakness_patterns=(
            r"\b(sole witness|uncorroborated|single source)\b",
            r"\b(inconsistent|contradicts|changed story|prior statement differs)\b",
        ),
        strength_title="Corroboration signals present",
        strength_detail="Independent sources or consistency references strengthen the prosecution narrative.",
        weakness_title="Corroboration or consistency concerns",
        weakness_detail="Single-witness cases or internal inconsistencies invite robust cross-examination.",
        bulletproof_action="Seek independent corroboration (CCTV, billing, GPS, third-party witnesses); reconcile inconsistencies early.",
        legal_anchor="Evidence Act; general principles on proof beyond reasonable doubt",
        kc_theme="Credibility and consistency",
    ),
    EvidenceRule(
        id="disclosure",
        category="Disclosure and unused material",
        strength_patterns=(
        r"\b(disclosure schedule|unused material|MG6|prosecution bundle)\b",
            r"\b(exculpatory|immaterial|reviewed by prosecutor)\b",
        ),
        weakness_patterns=(
            r"\b(not disclosed|late disclosure|missing pages|withheld)\b",
            r"\b(unreviewed material|unknown witness|undocumented interview)\b",
        ),
        strength_title="Disclosure process referenced",
        strength_detail="Mention of schedules or unused-material review supports fair-trial obligations.",
        weakness_title="Disclosure risk indicators",
        weakness_detail="Late or incomplete disclosure can collapse trials and invite abuse-of-process applications.",
        bulletproof_action="Complete unused-material review; update disclosure schedule; document all witness contacts.",
        legal_anchor="Constitution fair trial; criminal procedure disclosure duties",
        kc_theme="Disclosure failure",
    ),
    EvidenceRule(
        id="expert_evidence",
        category="Expert / forensic evidence",
        strength_patterns=(
            r"\b(expert report|qualifications|accredited lab|ISO 17025)\b",
            r"\b(methodology|peer review|control sample|calibration)\b",
        ),
        weakness_patterns=(
            r"\b(unqualified|informal opinion|no report|verbal opinion)\b",
            r"\b(no calibration|contaminated sample|broken procedure)\b",
        ),
        strength_title="Expert foundation referenced",
        strength_detail="Formal expert report or accredited laboratory references support Daubert-style scrutiny.",
        weakness_title="Expert evidence may lack foundation",
        weakness_detail="Informal opinions or procedural gaps in forensic handling are common attack lines.",
        bulletproof_action="Obtain full expert statement, CV, methodology, lab accreditation, and sample continuity.",
        legal_anchor="Evidence Act — opinion evidence and expert witnesses",
        kc_theme="Expert qualifications and methodology",
    ),
)


def count_pattern_matches(text: str, patterns: tuple[str, ...]) -> list[str]:
    text_lower = text.lower()
    hits: list[str] = []
    for pattern in patterns:
        if re.search(pattern, text_lower, re.I):
            hits.append(pattern)
    return hits


def detect_document_types(text: str) -> list[str]:
    mapping = {
        "Witness statement": r"\b(statement of|i (?:state|saw|observed)|deponent|affidavit)\b",
        "Scene notes / notebook": r"\b(notebook|scene visit|occurrence book|OB entry)\b",
        "Charge / indictment": r"\b(charge|indictment|information laid|count \d)\b",
        "Exhibit list": r"\b(exhibit [A-Z0-9]+|property register|seized items)\b",
        "Forensic report": r"\b(laboratory report|forensic|ballistics|DNA|toxicology)\b",
        "CCTV / video": r"\b(CCTV|footage|camera|DVR|video clip)\b",
        "Medical report": r"\b(medical report|post mortem|PM report|injury report|doctor)\b",
        "Disclosure schedule": r"\b(disclosure|unused material|schedule of evidence)\b",
    }
    found: list[str] = []
    for label, pattern in mapping.items():
        if re.search(pattern, text, re.I):
            found.append(label)
    return found

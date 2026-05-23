from __future__ import annotations

from .models import CrossExamQuestion, Finding, Severity


KC_QUESTION_BANK: dict[str, list[tuple[str, str, str]]] = {
    "Admissibility and fairness of statement": [
        (
            "Investigating officer",
            "Officer, before this statement was taken, what exact caution was administered—and where is that recorded?",
            "Tests whether caution and rights were properly given and documented.",
            "And if the recording equipment failed, why was the interview not paused until it was restored?",
        ),
        (
            "Investigating officer",
            "You rely on this statement, yet the defence says no contemporaneous recording exists—is that correct?",
            "Challenges reliability when only memory or unsigned notes exist.",
            "So the court is asked to accept your recollection of what was said days or weeks later?",
        ),
    ],
    "Chain of custody": [
        (
            "Property officer / exhibits officer",
            "Exhibit {exhibit}, as you call it—who had custody between seizure and the property room, and where is each signature?",
            "Exposes gaps in physical continuity.",
            "If the seal was broken, who authorised that, and was the defence notified?",
        ),
        (
            "First responding officer",
            "You say this item was seized at the scene—yet I see no photograph of the seal applied at that time. Why not?",
            "Undermines integrity where scene handling is undocumented.",
            "Could this item have been substituted before it reached the laboratory?",
        ),
    ],
    "Identification reliability": [
        (
            "Identifying witness",
            "You say you are sure—but you had only a brief glimpse in poor light, did you not?",
            "Classic Turnbull-style challenge on opportunity to observe.",
            "And you did not pick the accused out at a formal parade—you were shown a single photograph, were you not?",
        ),
        (
            "Investigating officer",
            "Why was no identification parade held when the suspect was available within 48 hours?",
            "Challenges failure to use best-practice ID procedure.",
            "Is it not true that a dock identification is the weakest form of identification?",
        ),
    ],
    "Digital authentication": [
        (
            "Digital forensic examiner",
            "Where is the SHA-256 hash of the extracted data, and who verified it on receipt at the lab?",
            "Tests whether digital evidence meets authentication standards.",
            "If all you have is a screenshot, how do you exclude the possibility of editing before capture?",
        ),
        (
            "Investigating officer",
            "This WhatsApp message—did you preserve the device forensically, or simply photograph the screen?",
            "Highlights weak capture methods common in messaging evidence.",
            "So the metadata, sender authentication, and chain of custody were never established?",
        ),
    ],
    "Hearsay and documentary foundation": [
        (
            "Document witness / records keeper",
            "Who created this document, and can that person attend to prove its contents?",
            "Challenges hearsay where maker is not called.",
            "This is a photocopy—where is the original, or the certificate permitting its use?",
        ),
    ],
    "Credibility and consistency": [
        (
            "Complainant / witness",
            "In your first account you said {detail_a}; today you say {detail_b}—which is true?",
            "Prior inconsistent statement attack.",
            "Were you trying to help the police, rather than tell the whole truth?",
        ),
        (
            "Investigating officer",
            "Apart from this witness, what independent evidence links the accused to the offence?",
            "Presses corroboration gap in single-witness cases.",
            "So the entire case rises or falls on one person's word?",
        ),
    ],
    "Disclosure failure": [
        (
            "Prosecutor / disclosure officer",
            "When did you first become aware of {material}, and why was it not on the initial disclosure schedule?",
            "Anticipates abuse-of-process and fair-trial challenges.",
            "Was this material capable of undermining the prosecution case or assisting the accused?",
        ),
    ],
    "Expert qualifications and methodology": [
        (
            "Forensic expert",
            "What accredited standard governs your method, and when was your equipment last calibrated?",
            "Challenges expert foundation under cross-examination.",
            "If contamination occurred at collection, would your results be meaningless?",
        ),
    ],
}


def generate_cross_examination(
    weaknesses: list[Finding],
    *,
    exhibit_label: str = "A",
    detail_a: str = "the incident occurred at 9 p.m.",
    detail_b: str = "10 p.m.",
    material: str = "the CCTV clip showing another person at the scene",
) -> list[CrossExamQuestion]:
    questions: list[CrossExamQuestion] = []
    seen_themes: set[str] = set()

    for weakness in weaknesses:
        theme = weakness.category if weakness.category in KC_QUESTION_BANK else _map_category_to_theme(
            weakness.category
        )
        if theme in seen_themes:
            continue
        bank = KC_QUESTION_BANK.get(theme)
        if not bank:
            continue
        seen_themes.add(theme)
        witness, question, purpose, follow_up = bank[0]
        questions.append(
            CrossExamQuestion(
                theme=theme,
                target_witness=witness,
                question=question.format(
                    exhibit=exhibit_label,
                    detail_a=detail_a,
                    detail_b=detail_b,
                    material=material,
                ),
                purpose=purpose,
                follow_up=follow_up.format(
                    exhibit=exhibit_label,
                    detail_a=detail_a,
                    detail_b=detail_b,
                    material=material,
                ),
            )
        )

    if not questions:
        questions.append(
            CrossExamQuestion(
                theme="General prosecution testing",
                target_witness="Investigating officer",
                question="Officer, having reviewed the file, what single piece of evidence, if disbelieved, would collapse your case?",
                purpose="Forces identification of the critical dependency — a standard senior-counsel stress test.",
                follow_up="And what have you done to independently verify that piece of evidence?",
            )
        )

    return questions


def _map_category_to_theme(category: str) -> str:
    aliases = {
        "Witness statements": "Admissibility and fairness of statement",
        "Exhibits and continuity": "Chain of custody",
        "Identification evidence": "Identification reliability",
        "Digital / cyber evidence": "Digital authentication",
        "Documentary / hearsay": "Hearsay and documentary foundation",
        "Corroboration and consistency": "Credibility and consistency",
        "Disclosure and unused material": "Disclosure failure",
        "Expert / forensic evidence": "Expert qualifications and methodology",
    }
    return aliases.get(category, category)


def weakness_to_severity(title: str) -> Severity:
    high_markers = ("disclosure", "chain", "identification", "hearsay", "digital")
    lowered = title.lower()
    if any(marker in lowered for marker in high_markers):
        return Severity.HIGH
    return Severity.MEDIUM

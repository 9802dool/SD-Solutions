from __future__ import annotations

import re
from dataclasses import dataclass

from .models import ExtractedFeature


@dataclass(frozen=True)
class FeatureVector:
    credible_eyewitnesses: float
    identification_quality: float
    forensic_dna: float
    forensic_fingerprint: float
    weapon_recovered: float
    confession_recorded: float
    cctv_present: float
    chain_of_custody: float
    statement_quality: float
    expert_forensic: float
    disclosure_complete: float
    hearsay_risk: float
    time_to_arrest_score: float

    def as_dict(self) -> dict[str, float]:
        return {
            "credible_eyewitnesses": self.credible_eyewitnesses,
            "identification_quality": self.identification_quality,
            "forensic_dna": self.forensic_dna,
            "forensic_fingerprint": self.forensic_fingerprint,
            "weapon_recovered": self.weapon_recovered,
            "confession_recorded": self.confession_recorded,
            "cctv_present": self.cctv_present,
            "chain_of_custody": self.chain_of_custody,
            "statement_quality": self.statement_quality,
            "expert_forensic": self.expert_forensic,
            "disclosure_complete": self.disclosure_complete,
            "hearsay_risk": self.hearsay_risk,
            "time_to_arrest_score": self.time_to_arrest_score,
        }

    def as_list(self) -> list[float]:
        return list(self.as_dict().values())


FEATURE_NAMES = list(FeatureVector(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0).as_dict().keys())


def _count(patterns: tuple[str, ...], text: str) -> int:
    return sum(1 for p in patterns if re.search(p, text, re.I))


def _bool(patterns: tuple[str, ...], text: str) -> float:
    return 1.0 if any(re.search(p, text, re.I) for p in patterns) else 0.0


def extract_features(text: str) -> tuple[FeatureVector, list[ExtractedFeature]]:
    """NLP + rule-based feature extraction from unstructured police narratives."""
    lower = text.lower()
    details: list[ExtractedFeature] = []

    witness_terms = (
        r"\b(independent witness|eyewitness|credible witness|corroborated witness)\b",
        r"\b(multiple witnesses|two witnesses|three witnesses)\b",
    )
    witness_hits = _count(witness_terms, lower)
    witness_count = min(3.0, witness_hits + (1.0 if re.search(r"\bwitness\b", lower) else 0.0))
    details.append(
        ExtractedFeature(
            "credible_eyewitnesses",
            witness_count,
            f"{witness_count:.0f} eyewitness signal(s)",
            "nlp",
        )
    )

    id_good = _bool(
        (
            r"\b(identification parade|line[- ]?up|CCTV (still|footage)|Turnbull)\b",
            r"\b(independent witness|multiple witnesses)\b",
        ),
        lower,
    )
    id_bad = _bool(
        (
            r"\b(show[- ]?up|single photo|brief glimpse|poor lighting|one witness only)\b",
        ),
        lower,
    )
    identification_quality = max(0.0, min(1.0, id_good - 0.5 * id_bad))
    details.append(
        ExtractedFeature(
            "identification_quality",
            identification_quality,
            "Identification procedure quality (0–1)",
            "nlp",
        )
    )

    forensic_dna = _bool((r"\b(DNA|genetic profile|STR profile)\b",), lower)
    forensic_fingerprint = _bool((r"\b(fingerprint|latent print|AFIS)\b",), lower)
    weapon_recovered = _bool((r"\b(firearm recovered|weapon seized|knife recovered|gun found)\b",), lower)
    confession_recorded = _bool(
        (r"\b(confession|admission|recorded interview|caution administered)\b",),
        lower,
    )
    cctv_present = _bool((r"\b(CCTV|footage|DVR|video clip)\b",), lower)

    chain_good = _bool(
        (r"\b(chain of custody|sealed bag|custody log|property room)\b",),
        lower,
    )
    chain_bad = _bool((r"\b(gap in custody|unsealed|broken seal|no continuity)\b",), lower)
    chain_of_custody = max(0.0, min(1.0, chain_good - 0.6 * chain_bad))

    stmt_good = _bool(
        (r"\b(recorded interview|signed statement|contemporaneous notes)\b",),
        lower,
    )
    stmt_bad = _bool((r"\b(verbal only|unsigned|not recorded|no caution)\b",), lower)
    statement_quality = max(0.0, min(1.0, stmt_good - 0.6 * stmt_bad))

    expert_forensic = _bool(
        (r"\b(expert report|forensic examiner|laboratory report|ISO 17025)\b",),
        lower,
    )
    disclosure_complete = _bool(
        (r"\b(disclosure schedule|unused material|prosecution bundle)\b",),
        lower,
    )
    hearsay_risk = _bool(
        (r"\b(hearsay|someone told me|rumour|second[- ]hand)\b",),
        lower,
    )

    time_match = re.search(
        r"\b(within (\d+) (hours?|days?)|(\d+) hours? (later|after)|same day arrest)\b",
        lower,
    )
    time_to_arrest_score = 0.5
    if time_match:
        time_to_arrest_score = 0.9 if "hour" in time_match.group(0) or "same day" in time_match.group(0) else 0.7
    if re.search(r"\b(months? later|years? later|delayed arrest)\b", lower):
        time_to_arrest_score = 0.2

    for name, value, label in (
        ("forensic_dna", forensic_dna, "DNA / genetic evidence"),
        ("forensic_fingerprint", forensic_fingerprint, "Fingerprint evidence"),
        ("weapon_recovered", weapon_recovered, "Weapon recovered"),
        ("confession_recorded", confession_recorded, "Recorded confession / interview"),
        ("cctv_present", cctv_present, "CCTV / video evidence"),
        ("chain_of_custody", chain_of_custody, "Chain of custody integrity"),
        ("statement_quality", statement_quality, "Witness statement quality"),
        ("expert_forensic", expert_forensic, "Expert / lab report"),
        ("disclosure_complete", disclosure_complete, "Disclosure schedule present"),
        ("hearsay_risk", hearsay_risk, "Hearsay risk indicator"),
        ("time_to_arrest_score", time_to_arrest_score, "Timeliness of arrest (proxy)"),
    ):
        details.append(ExtractedFeature(name, value, label, "nlp"))

    vector = FeatureVector(
        credible_eyewitnesses=witness_count,
        identification_quality=identification_quality,
        forensic_dna=forensic_dna,
        forensic_fingerprint=forensic_fingerprint,
        weapon_recovered=weapon_recovered,
        confession_recorded=confession_recorded,
        cctv_present=cctv_present,
        chain_of_custody=chain_of_custody,
        statement_quality=statement_quality,
        expert_forensic=expert_forensic,
        disclosure_complete=disclosure_complete,
        hearsay_risk=hearsay_risk,
        time_to_arrest_score=time_to_arrest_score,
    )
    return vector, details

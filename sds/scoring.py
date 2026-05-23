from __future__ import annotations

from .features import FeatureVector
from .models import MissingElement, Severity, WeightedScore

# Evidence weights — high for forensic/DNA, lower for circumstantial signals.
EVIDENCE_WEIGHTS: dict[str, tuple[float, str]] = {
    "forensic_dna": (0.95, "DNA / genetic evidence"),
    "forensic_fingerprint": (0.85, "Fingerprint evidence"),
    "confession_recorded": (0.80, "Recorded confession (lawfully obtained)"),
    "cctv_present": (0.75, "CCTV / video corroboration"),
    "weapon_recovered": (0.70, "Physical weapon link"),
    "credible_eyewitnesses": (0.65, "Independent eyewitnesses"),
    "identification_quality": (0.60, "Identification procedure quality"),
    "expert_forensic": (0.60, "Expert / laboratory report"),
    "chain_of_custody": (0.55, "Exhibit continuity"),
    "statement_quality": (0.50, "Statement process quality"),
    "disclosure_complete": (0.45, "Disclosure completeness"),
    "time_to_arrest_score": (0.35, "Investigation timeliness"),
    "hearsay_risk": (-0.50, "Hearsay exposure (penalty)"),
}

CONVICTION_REQUIREMENTS: tuple[tuple[str, str, Severity, str], ...] = (
    (
        "forensic_dna",
        "Forensic link (DNA, fingerprint, or expert report)",
        Severity.HIGH,
        "No clear forensic or expert laboratory link detected in the file text.",
    ),
    (
        "credible_eyewitnesses",
        "Independent eyewitness or strong identification",
        Severity.HIGH,
        "No credible eyewitness or robust identification procedure referenced.",
    ),
    (
        "chain_of_custody",
        "Exhibit chain of custody",
        Severity.MEDIUM,
        "Continuity of physical exhibits is not documented in the uploaded text.",
    ),
    (
        "statement_quality",
        "Lawful recorded statement",
        Severity.MEDIUM,
        "No indication of a properly recorded and cautioned statement.",
    ),
    (
        "disclosure_complete",
        "Disclosure schedule",
        Severity.MEDIUM,
        "Disclosure / unused-material review not evidenced in the bundle.",
    ),
)


def compute_weighted_scores(vector: FeatureVector) -> list[WeightedScore]:
    features = vector.as_dict()
    scores: list[WeightedScore] = []

    for key, (weight, label) in EVIDENCE_WEIGHTS.items():
        raw = features[key]
        if key == "credible_eyewitnesses":
            normalized = min(1.0, raw / 3.0)
        elif key == "hearsay_risk":
            normalized = raw
            contribution = weight * normalized
            scores.append(
                WeightedScore(
                    category=label,
                    weight=weight,
                    score=normalized,
                    weighted_contribution=contribution,
                    note="Penalty applied when hearsay language appears.",
                )
            )
            continue
        else:
            normalized = max(0.0, min(1.0, raw))

        contribution = weight * normalized
        scores.append(
            WeightedScore(
                category=label,
                weight=weight,
                score=normalized,
                weighted_contribution=contribution,
                note=f"Weighted contribution: {contribution:.2f}",
            )
        )

    scores.sort(key=lambda s: abs(s.weighted_contribution), reverse=True)
    return scores


def composite_score_from_weights(scores: list[WeightedScore]) -> int:
    total_weight = sum(abs(s.weight) for s in scores if s.weight > 0)
    if total_weight == 0:
        return 0
    raw = sum(s.weighted_contribution for s in scores)
    max_possible = total_weight
    pct = (raw / max_possible) * 100
    return max(0, min(100, round(pct)))


def detect_missing_elements(vector: FeatureVector) -> list[MissingElement]:
    features = vector.as_dict()
    missing: list[MissingElement] = []

    forensic_ok = (
        features["forensic_dna"] >= 1
        or features["forensic_fingerprint"] >= 1
        or features["expert_forensic"] >= 1
    )
    witness_ok = features["credible_eyewitnesses"] >= 1 or features["identification_quality"] >= 0.5

    checks = {
        "forensic_dna": forensic_ok,
        "credible_eyewitnesses": witness_ok,
        "chain_of_custody": features["chain_of_custody"] >= 0.5,
        "statement_quality": features["statement_quality"] >= 0.5,
        "disclosure_complete": features["disclosure_complete"] >= 1,
    }

    for key, label, severity, detail in CONVICTION_REQUIREMENTS:
        if not checks.get(key, False):
            missing.append(MissingElement(element=label, severity=severity, detail=detail))

    return missing

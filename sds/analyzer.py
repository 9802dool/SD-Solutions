from __future__ import annotations

from .evidence_rules import EVIDENCE_RULES, count_pattern_matches, detect_document_types
from .kc_cross_exam import generate_cross_examination, weakness_to_severity
from .models import (
    AnalysisReport,
    DocumentSummary,
    Finding,
    ReadinessBand,
    Recommendation,
    Severity,
)

DISCLAIMER = (
    "SD SOLUTIONS (SDS) — DECISION-SUPPORT ONLY. NOT LEGAL ADVICE. "
    "All outputs require review by qualified legal counsel. "
    "Do not rely on automated analysis for charging, disclosure, or court decisions."
)


def analyze_case(
    documents: dict[str, str],
    *,
    case_reference: str = "UNASSIGNED",
) -> AnalysisReport:
    if not documents:
        raise ValueError("At least one document is required.")

    combined_text = "\n\n".join(documents.values())
    summaries: list[DocumentSummary] = []
    strengths: list[Finding] = []
    weaknesses: list[Finding] = []
    recommendations: list[Recommendation] = []
    seen_recommendations: set[str] = set()

    for filename, text in documents.items():
        detected = tuple(detect_document_types(text))
        summaries.append(
            DocumentSummary(
                filename=filename,
                kind=detected[0] if detected else "General document",
                word_count=len(text.split()),
                detected_types=detected or ("General document",),
            )
        )

    for rule in EVIDENCE_RULES:
        strength_hits = count_pattern_matches(combined_text, rule.strength_patterns)
        weakness_hits = count_pattern_matches(combined_text, rule.weakness_patterns)

        if strength_hits and len(strength_hits) >= len(weakness_hits):
            strengths.append(
                Finding(
                    category=rule.category,
                    title=rule.strength_title,
                    detail=rule.strength_detail,
                    severity=Severity.LOW,
                    evidence_refs=tuple(strength_hits[:3]),
                )
            )
        elif weakness_hits:
            weaknesses.append(
                Finding(
                    category=rule.category,
                    title=rule.weakness_title,
                    detail=rule.weakness_detail,
                    severity=weakness_to_severity(rule.weakness_title),
                    evidence_refs=tuple(weakness_hits[:3]),
                )
            )
            if rule.bulletproof_action not in seen_recommendations:
                seen_recommendations.add(rule.bulletproof_action)
                recommendations.append(
                    Recommendation(
                        priority=_priority_for_category(rule.category),
                        action=rule.bulletproof_action,
                        rationale=rule.weakness_detail,
                        legal_anchor=rule.legal_anchor,
                    )
                )
        elif not strength_hits:
            weaknesses.append(
                Finding(
                    category=rule.category,
                    title=f"No clear signals for {rule.category.lower()}",
                    detail=(
                        f"The uploaded bundle does not mention standard indicators for {rule.category.lower()}. "
                        "Absence in text does not prove a gap in the real file — verify manually."
                    ),
                    severity=Severity.MEDIUM,
                )
            )
            if rule.bulletproof_action not in seen_recommendations:
                seen_recommendations.add(rule.bulletproof_action)
                recommendations.append(
                    Recommendation(
                        priority=_priority_for_category(rule.category) + 1,
                        action=f"Confirm on file: {rule.bulletproof_action}",
                        rationale="Checklist item not evidenced in uploaded text.",
                        legal_anchor=rule.legal_anchor,
                    )
                )

    recommendations.sort(key=lambda item: item.priority)
    recommendations = _renumber_recommendations(recommendations)
    cross_examination = generate_cross_examination(weaknesses)

    readiness_score = max(0, min(100, 55 + len(strengths) * 8 - len(weaknesses) * 7))
    readiness_band = _score_to_band(readiness_score)

    high_weaknesses = sum(1 for item in weaknesses if item.severity == Severity.HIGH)
    summary = (
        f"Case `{case_reference}`: {len(documents)} document(s) analysed. "
        f"{len(strengths)} strength signal(s), {len(weaknesses)} weakness or gap signal(s) "
        f"({high_weaknesses} high severity). "
        f"Overall readiness: {readiness_band.value} ({readiness_score}/100). "
        "Use cross-examination questions to stress-test before trial."
    )

    return AnalysisReport(
        case_reference=case_reference,
        documents=summaries,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        cross_examination=cross_examination,
        readiness_band=readiness_band,
        readiness_score=readiness_score,
        summary=summary,
        disclaimer=DISCLAIMER,
    )


def _priority_for_category(category: str) -> int:
    order = {
        "Disclosure and unused material": 1,
        "Exhibits and continuity": 2,
        "Identification evidence": 3,
        "Witness statements": 4,
        "Digital / cyber evidence": 5,
        "Expert / forensic evidence": 6,
        "Documentary / hearsay": 7,
        "Corroboration and consistency": 8,
    }
    return order.get(category, 9)


def _renumber_recommendations(items: list[Recommendation]) -> list[Recommendation]:
    renumbered: list[Recommendation] = []
    for idx, item in enumerate(items, 1):
        renumbered.append(
            Recommendation(
                priority=idx,
                action=item.action,
                rationale=item.rationale,
                legal_anchor=item.legal_anchor,
            )
        )
    return renumbered


def _score_to_band(score: int) -> ReadinessBand:
    if score >= 75:
        return ReadinessBand.STRONG
    if score >= 50:
        return ReadinessBand.DEVELOPING
    return ReadinessBand.AT_RISK


def report_to_markdown(report: AnalysisReport) -> str:
    lines: list[str] = [
        f"# SDS case analysis report — {report.case_reference}",
        "",
        report.summary,
        "",
        f"**Readiness band:** {report.readiness_band.value} ({report.readiness_score}/100)",
        "",
        "## Documents analysed",
    ]

    for doc in report.documents:
        types = ", ".join(doc.detected_types)
        lines.append(f"- **{doc.filename}** ({doc.word_count} words) — {types}")

    lines.extend(["", "## Strengths"])
    for item in report.strengths:
        lines.append(f"- **{item.title}** ({item.category}): {item.detail}")

    lines.extend(["", "## Weaknesses and gaps"])
    for item in report.weaknesses:
        lines.append(
            f"- **[{item.severity.value.upper()}] {item.title}** ({item.category}): {item.detail}"
        )

    lines.extend(["", "## Bulletproofing recommendations"])
    for rec in report.recommendations:
        lines.append(
            f"{rec.priority}. **{rec.action}** — {rec.rationale} *(Ref: {rec.legal_anchor})*"
        )

    lines.extend(["", "## Anticipated King's Counsel cross-examination"])
    for idx, q in enumerate(report.cross_examination, 1):
        lines.extend(
            [
                f"### {idx}. {q.theme}",
                f"- **Target:** {q.target_witness}",
                f"- **Question:** {q.question}",
                f"- **Purpose:** {q.purpose}",
                f"- **Follow-up:** {q.follow_up}",
                "",
            ]
        )

    lines.extend(["---", report.disclaimer])
    return "\n".join(lines)

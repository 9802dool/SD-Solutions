from __future__ import annotations

from .evidence_rules import EVIDENCE_RULES, count_pattern_matches, detect_document_types
from .features import extract_features
from .kc_cross_exam import generate_cross_examination, weakness_to_severity
from .ml_model import BIAS_NOTICE, predict_conviction_strength
from .models import (
    AnalysisReport,
    DocumentSummary,
    Finding,
    ReadinessBand,
    Recommendation,
    Severity,
)
from .scoring import (
    composite_score_from_weights,
    compute_weighted_scores,
    detect_missing_elements,
)

DISCLAIMER = (
    "SD SOLUTIONS (SDS) — DECISION-SUPPORT ONLY. NOT LEGAL ADVICE. "
    "All outputs require review by qualified legal counsel. "
    "Do not rely on automated analysis, NLP extraction, or ML confidence scores "
    "for charging, disclosure, or court decisions. Human professional review is mandatory."
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

    feature_vector, extracted_features = extract_features(combined_text)
    weighted_scores = compute_weighted_scores(feature_vector)
    missing_elements = detect_missing_elements(feature_vector)
    model_prediction = predict_conviction_strength(feature_vector)
    composite = composite_score_from_weights(weighted_scores)

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

    for gap in missing_elements:
        recommendations.insert(
            0,
            Recommendation(
                priority=0,
                action=f"Close conviction gap: {gap.element}",
                rationale=gap.detail,
                legal_anchor="Prosecution case preparation — proof beyond reasonable doubt",
            ),
        )

    recommendations.sort(key=lambda item: item.priority)
    recommendations = _renumber_recommendations(recommendations)
    cross_examination = generate_cross_examination(weaknesses)

    rule_score = max(0, min(100, 55 + len(strengths) * 8 - len(weaknesses) * 7))
    readiness_score = round((composite + rule_score) / 2)
    readiness_band = _score_to_band(readiness_score)

    high_weaknesses = sum(1 for item in weaknesses if item.severity == Severity.HIGH)
    ml_pct = model_prediction.conviction_probability * 100
    summary = (
        f"Case `{case_reference}`: {len(documents)} document(s) analysed. "
        f"ML conviction confidence: {model_prediction.confidence_label} ({ml_pct:.0f}%) via {model_prediction.model_name}. "
        f"Composite evidence score: {readiness_score}/100 ({readiness_band.value}). "
        f"{len(strengths)} rule strength(s), {len(weaknesses)} weakness/gap signal(s) ({high_weaknesses} high). "
        f"{len(missing_elements)} potential conviction gap(s) flagged. Human review required."
    )

    return AnalysisReport(
        case_reference=case_reference,
        documents=summaries,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        cross_examination=cross_examination,
        extracted_features=extracted_features,
        weighted_scores=weighted_scores,
        missing_elements=missing_elements,
        model_prediction=model_prediction,
        readiness_band=readiness_band,
        readiness_score=readiness_score,
        composite_score=composite,
        summary=summary,
        bias_notice=BIAS_NOTICE,
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
    ]

    if report.model_prediction:
        mp = report.model_prediction
        lines.extend(
            [
                "",
                "## ML conviction confidence (supportive only)",
                f"- **Label:** {mp.confidence_label}",
                f"- **Probability:** {mp.conviction_probability * 100:.1f}%",
                f"- **Model:** {mp.model_name}",
                f"- **Human oversight required:** {'Yes' if mp.human_oversight_required else 'No'}",
            ]
        )

    lines.extend(["", "## NLP extracted features"])
    for feat in report.extracted_features:
        lines.append(f"- **{feat.label}:** {feat.value:.2f} ({feat.source})")

    lines.extend(["", "## Weighted evidence scores"])
    for ws in report.weighted_scores:
        lines.append(
            f"- **{ws.category}** (weight {ws.weight:.2f}): score {ws.score:.2f} -> {ws.weighted_contribution:+.2f}"
        )

    if report.missing_elements:
        lines.extend(["", "## Missing conviction elements"])
        for gap in report.missing_elements:
            lines.append(f"- **[{gap.severity.value.upper()}] {gap.element}:** {gap.detail}")

    lines.extend(["", "## Documents analysed"])
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

    lines.extend(["", "## Bias and fairness notice", report.bias_notice, "", "---", report.disclaimer])
    return "\n".join(lines)

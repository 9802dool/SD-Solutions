from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ReadinessBand(str, Enum):
    STRONG = "STRONG"
    DEVELOPING = "DEVELOPING"
    AT_RISK = "AT_RISK"


class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class DocumentSummary:
    filename: str
    kind: str
    word_count: int
    detected_types: tuple[str, ...]


@dataclass(frozen=True)
class Finding:
    category: str
    title: str
    detail: str
    severity: Severity
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class Recommendation:
    priority: int
    action: str
    rationale: str
    legal_anchor: str


@dataclass(frozen=True)
class CrossExamQuestion:
    theme: str
    target_witness: str
    question: str
    purpose: str
    follow_up: str


@dataclass(frozen=True)
class ExtractedFeature:
    name: str
    value: float
    label: str
    source: str  # nlp | rule


@dataclass(frozen=True)
class WeightedScore:
    category: str
    weight: float
    score: float
    weighted_contribution: float
    note: str


@dataclass(frozen=True)
class MissingElement:
    element: str
    severity: Severity
    detail: str


@dataclass(frozen=True)
class ModelPrediction:
    conviction_probability: float
    confidence_label: str
    model_name: str
    human_oversight_required: bool = True


@dataclass(frozen=True)
class LegalCrossReference:
    citation: str
    section_ref: str
    source_title: str
    title: str
    summary: str
    relevance: str


@dataclass
class AnalysisReport:
    case_reference: str
    documents: list[DocumentSummary] = field(default_factory=list)
    strengths: list[Finding] = field(default_factory=list)
    weaknesses: list[Finding] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    cross_examination: list[CrossExamQuestion] = field(default_factory=list)
    extracted_features: list[ExtractedFeature] = field(default_factory=list)
    weighted_scores: list[WeightedScore] = field(default_factory=list)
    missing_elements: list[MissingElement] = field(default_factory=list)
    legal_cross_references: list[LegalCrossReference] = field(default_factory=list)
    model_prediction: ModelPrediction | None = None
    readiness_band: ReadinessBand = ReadinessBand.DEVELOPING
    readiness_score: int = 0
    composite_score: int = 0
    summary: str = ""
    bias_notice: str = ""
    disclaimer: str = ""

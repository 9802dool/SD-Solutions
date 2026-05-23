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


@dataclass
class AnalysisReport:
    case_reference: str
    documents: list[DocumentSummary] = field(default_factory=list)
    strengths: list[Finding] = field(default_factory=list)
    weaknesses: list[Finding] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    cross_examination: list[CrossExamQuestion] = field(default_factory=list)
    readiness_band: ReadinessBand = ReadinessBand.DEVELOPING
    readiness_score: int = 0
    summary: str = ""
    disclaimer: str = ""

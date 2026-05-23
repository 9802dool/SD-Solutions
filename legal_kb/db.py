from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "legal" / "tt_legal.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS legal_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL,
    citation TEXT NOT NULL UNIQUE,
    jurisdiction TEXT NOT NULL DEFAULT 'Trinidad and Tobago',
    official_url TEXT,
    summary TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS legal_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL REFERENCES legal_sources(id) ON DELETE CASCADE,
    section_ref TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    keywords TEXT NOT NULL DEFAULT '',
    evidence_tags TEXT NOT NULL DEFAULT '',
    full_text TEXT,
    UNIQUE(source_id, section_ref)
);

CREATE INDEX IF NOT EXISTS idx_sections_tags ON legal_sections(evidence_tags);
CREATE INDEX IF NOT EXISTS idx_sections_keywords ON legal_sections(keywords);
"""


@dataclass(frozen=True)
class LegalSource:
    id: int
    title: str
    source_type: str
    citation: str
    jurisdiction: str
    official_url: str | None
    summary: str | None


@dataclass(frozen=True)
class LegalSection:
    id: int
    source_id: int
    section_ref: str
    title: str
    summary: str
    keywords: str
    evidence_tags: str
    full_text: str | None
    citation: str
    source_title: str


class LegalDatabase:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_DB
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def add_source(
        self,
        *,
        title: str,
        source_type: str,
        citation: str,
        jurisdiction: str = "Trinidad and Tobago",
        official_url: str | None = None,
        summary: str | None = None,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO legal_sources (title, source_type, citation, jurisdiction, official_url, summary)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(citation) DO UPDATE SET
                    title=excluded.title,
                    source_type=excluded.source_type,
                    jurisdiction=excluded.jurisdiction,
                    official_url=excluded.official_url,
                    summary=excluded.summary
                """,
                (title, source_type, citation, jurisdiction, official_url, summary),
            )
            conn.commit()
            row = conn.execute(
                "SELECT id FROM legal_sources WHERE citation = ?", (citation,)
            ).fetchone()
            return int(row["id"])

    def add_section(
        self,
        *,
        citation: str,
        section_ref: str,
        title: str,
        summary: str,
        keywords: str = "",
        evidence_tags: str = "",
        full_text: str | None = None,
    ) -> int:
        source_id = self._source_id_by_citation(citation)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO legal_sections
                (source_id, section_ref, title, summary, keywords, evidence_tags, full_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, section_ref) DO UPDATE SET
                    title=excluded.title,
                    summary=excluded.summary,
                    keywords=excluded.keywords,
                    evidence_tags=excluded.evidence_tags,
                    full_text=excluded.full_text
                """,
                (source_id, section_ref, title, summary, keywords, evidence_tags, full_text),
            )
            conn.commit()
            row = conn.execute(
                """
                SELECT s.id FROM legal_sections s
                JOIN legal_sources src ON src.id = s.source_id
                WHERE src.citation = ? AND s.section_ref = ?
                """,
                (citation, section_ref),
            ).fetchone()
            return int(row["id"])

    def _source_id_by_citation(self, citation: str) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id FROM legal_sources WHERE citation = ?", (citation,)
            ).fetchone()
            if not row:
                raise ValueError(f"Unknown legal source citation: {citation}")
            return int(row["id"])

    def list_sources(self) -> list[LegalSource]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM legal_sources ORDER BY title").fetchall()
        return [self._row_to_source(r) for r in rows]

    def list_sections(self, *, citation: str | None = None) -> list[LegalSection]:
        query = """
            SELECT s.*, src.citation, src.title AS source_title
            FROM legal_sections s
            JOIN legal_sources src ON src.id = s.source_id
        """
        params: tuple = ()
        if citation:
            query += " WHERE src.citation = ?"
            params = (citation,)
        query += " ORDER BY src.title, s.section_ref"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_section(r) for r in rows]

    def search(self, query: str, limit: int = 20) -> list[LegalSection]:
        like = f"%{query.lower()}%"
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT s.*, src.citation, src.title AS source_title
                FROM legal_sections s
                JOIN legal_sources src ON src.id = s.source_id
                WHERE lower(s.title) LIKE ?
                   OR lower(s.summary) LIKE ?
                   OR lower(s.keywords) LIKE ?
                   OR lower(s.evidence_tags) LIKE ?
                   OR lower(s.section_ref) LIKE ?
                ORDER BY s.id
                LIMIT ?
                """,
                (like, like, like, like, like, limit),
            ).fetchall()
        return [self._row_to_section(r) for r in rows]

    def sections_by_tags(self, tags: list[str]) -> list[LegalSection]:
        if not tags:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT s.*, src.citation, src.title AS source_title
                FROM legal_sections s
                JOIN legal_sources src ON src.id = s.source_id
                """
            ).fetchall()
        results: list[LegalSection] = []
        tag_set = {t.lower() for t in tags}
        for row in rows:
            section_tags = {t.strip().lower() for t in row["evidence_tags"].split(",") if t.strip()}
            if tag_set & section_tags:
                results.append(self._row_to_section(row))
        return results

    def import_markdown_file(
        self,
        path: Path,
        *,
        citation: str,
        source_type: str = "act",
        title: str | None = None,
    ) -> int:
        """Parse markdown with ## section headings into legal_sections rows."""
        text = path.read_text(encoding="utf-8", errors="replace")
        source_title = title or path.stem.replace("-", " ").title()
        source_id = self.add_source(
            title=source_title,
            source_type=source_type,
            citation=citation,
            summary=f"Imported from {path.name}",
        )
        current_ref = "intro"
        current_title = "Introduction"
        buffer: list[str] = []

        def flush() -> None:
            nonlocal buffer, current_ref, current_title
            body = "\n".join(buffer).strip()
            if body:
                with self._connect() as conn:
                    conn.execute(
                        """
                        INSERT INTO legal_sections
                        (source_id, section_ref, title, summary, keywords, evidence_tags, full_text)
                        VALUES (?, ?, ?, ?, '', '', ?)
                        ON CONFLICT(source_id, section_ref) DO UPDATE SET
                            title=excluded.title,
                            summary=excluded.summary,
                            full_text=excluded.full_text
                        """,
                        (source_id, current_ref, current_title, body[:500], body),
                    )
                    conn.commit()
            buffer = []

        for line in text.splitlines():
            if line.startswith("## "):
                flush()
                heading = line[3:].strip()
                if "|" in heading:
                    current_ref, current_title = [p.strip() for p in heading.split("|", 1)]
                else:
                    current_ref = heading.split()[0].lower().replace(".", "-")
                    current_title = heading
            else:
                buffer.append(line)
        flush()
        return source_id

    def export_json(self, out_path: Path) -> None:
        import json

        payload = {
            "jurisdiction": "Trinidad and Tobago",
            "sources": [
                {
                    "id": s.id,
                    "title": s.title,
                    "sourceType": s.source_type,
                    "citation": s.citation,
                    "jurisdiction": s.jurisdiction,
                    "officialUrl": s.official_url,
                    "summary": s.summary,
                }
                for s in self.list_sources()
            ],
            "sections": [
                {
                    "id": sec.id,
                    "citation": sec.citation,
                    "sourceTitle": sec.source_title,
                    "sectionRef": sec.section_ref,
                    "title": sec.title,
                    "summary": sec.summary,
                    "keywords": sec.keywords,
                    "evidenceTags": [t.strip() for t in sec.evidence_tags.split(",") if t.strip()],
                    "fullText": sec.full_text,
                }
                for sec in self.list_sections()
            ],
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def _row_to_source(row: sqlite3.Row) -> LegalSource:
        return LegalSource(
            id=int(row["id"]),
            title=str(row["title"]),
            source_type=str(row["source_type"]),
            citation=str(row["citation"]),
            jurisdiction=str(row["jurisdiction"]),
            official_url=row["official_url"],
            summary=row["summary"],
        )

    @staticmethod
    def _row_to_section(row: sqlite3.Row) -> LegalSection:
        return LegalSection(
            id=int(row["id"]),
            source_id=int(row["source_id"]),
            section_ref=str(row["section_ref"]),
            title=str(row["title"]),
            summary=str(row["summary"]),
            keywords=str(row["keywords"]),
            evidence_tags=str(row["evidence_tags"]),
            full_text=row["full_text"],
            citation=str(row["citation"]),
            source_title=str(row["source_title"]),
        )

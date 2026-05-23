from __future__ import annotations

from pathlib import Path


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".csv", ".log"}:
        return read_text_file(path)

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "PDF support requires `pypdf`. Install with: pip install pypdf"
            ) from exc
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    if suffix in {".docx", ".doc"}:
        try:
            import docx  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Word support requires `python-docx`. Install with: pip install python-docx"
            ) from exc
        document = docx.Document(str(path))
        return "\n".join(p.text for p in document.paragraphs)

    raise ValueError(
        f"Unsupported file type `{suffix}`. Use .txt, .md, .pdf, or .docx."
    )


def ingest_uploads(paths: list[Path]) -> dict[str, str]:
    corpus: dict[str, str] = {}
    for path in paths:
        corpus[path.name] = extract_text(path)
    return corpus

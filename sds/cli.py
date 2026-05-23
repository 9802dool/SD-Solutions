#!/usr/bin/env python3
"""
SD Solutions (SDS) — CLI.

Upload police documents and evidence bundles to receive:
  - strength / weakness signals
  - bulletproofing recommendations
  - anticipated King's Counsel cross-examination questions

Usage:
  python -m sds --case CR-2026-001 file1.txt file2.pdf
  python -m sds --demo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyzer import analyze_case, report_to_markdown
from .ingest import ingest_uploads
from .report_docx import write_report_docx


def _demo_documents() -> dict[str, str]:
    return {
        "scene_notes.txt": """
        PC 4521 scene visit notebook entry.
        Complainant stated suspect known by nickname only.
        Item seized — mobile phone — unsealed bag used due to rain.
        No CCTV recovered yet. Verbal account only; statement not recorded.
        """,
        "witness_summary.txt": """
        Single witness — brief glimpse at night, poor street lighting.
        Show-up identification at station using one photograph.
        Someone told officer the accused was involved (hearsay).
        """,
        "exhibit_list.txt": """
        Exhibit A mobile phone — gap in custody between scene and property room noted.
        Screenshot of WhatsApp message saved; no hash value or forensic extraction.
        """,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SD Solutions (SDS) — analyse case documents for readiness."
    )
    parser.add_argument("files", nargs="*", help="Document paths (.txt, .pdf, .docx)")
    parser.add_argument("--case", default="DEMO-CASE", help="Case reference / OC number")
    parser.add_argument("--demo", action="store_true", help="Run built-in demo bundle")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write report (.docx or .md)",
    )
    args = parser.parse_args()

    if args.demo:
        documents = _demo_documents()
    elif args.files:
        paths = [Path(item) for item in args.files]
        for path in paths:
            if not path.exists():
                print(f"File not found: {path}", file=sys.stderr)
                sys.exit(1)
        documents = ingest_uploads(paths)
    else:
        parser.print_help()
        sys.exit(1)

    report = analyze_case(documents, case_reference=args.case)
    markdown = report_to_markdown(report)
    print(markdown)

    if args.output:
        if args.output.suffix.lower() == ".docx":
            write_report_docx(report, args.output)
        else:
            args.output.write_text(markdown, encoding="utf-8")
        print(f"\nReport written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()

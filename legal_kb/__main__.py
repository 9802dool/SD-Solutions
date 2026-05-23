#!/usr/bin/env python3
"""Manage the Trinidad & Tobago legal knowledge base for SDS."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .cross_reference import cross_reference_case
from .db import LegalDatabase
from .seed import seed_tt_legal_kb

WEB_EXPORT = Path(__file__).resolve().parents[1] / "web" / "public" / "legal" / "kb.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="SDS Legal Knowledge Base (Trinidad & Tobago)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create database and seed TT legal summaries")

    import_cmd = sub.add_parser("import", help="Import a markdown law file")
    import_cmd.add_argument("file", type=Path)
    import_cmd.add_argument("--citation", required=True)
    import_cmd.add_argument("--title")
    import_cmd.add_argument("--type", default="act")

    list_cmd = sub.add_parser("list", help="List sources or sections")
    list_cmd.add_argument("--citation", help="Filter sections by source citation")

    search_cmd = sub.add_parser("search", help="Search legal sections")
    search_cmd.add_argument("query")

    export_cmd = sub.add_parser("export", help="Export JSON for the web app")
    export_cmd.add_argument("--out", type=Path, default=WEB_EXPORT)

    args = parser.parse_args()
    db = LegalDatabase()

    if args.command == "init":
        seed_tt_legal_kb(db)
        db.export_json(WEB_EXPORT)
        print(f"Seeded TT legal KB -> {db.path}")
        print(f"Exported web JSON -> {WEB_EXPORT}")
        return

    if args.command == "import":
        if not args.file.exists():
            print(f"File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        db.import_markdown_file(
            args.file,
            citation=args.citation,
            source_type=args.type,
            title=args.title,
        )
        db.export_json(WEB_EXPORT)
        print(f"Imported {args.file} under citation {args.citation}")
        print(f"Updated web JSON -> {WEB_EXPORT}")
        return

    if args.command == "list":
        if args.citation:
            for sec in db.list_sections(citation=args.citation):
                print(f"[{sec.citation} {sec.section_ref}] {sec.title}")
        else:
            for src in db.list_sources():
                print(f"{src.citation} — {src.title} ({src.source_type})")
        return

    if args.command == "search":
        for sec in db.search(args.query):
            print(f"[{sec.citation} {sec.section_ref}] {sec.title}")
            print(f"  {sec.summary[:120]}...")
        return

    if args.command == "export":
        db.export_json(args.out)
        print(f"Exported -> {args.out}")


if __name__ == "__main__":
    main()

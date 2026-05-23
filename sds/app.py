#!/usr/bin/env python3
"""
Streamlit UI for SD Solutions (SDS).

Run from project root:
  pip install -r requirements.txt
  streamlit run sds/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from sds.analyzer import analyze_case, report_to_markdown
from sds.ingest import extract_text
from sds.report_docx import report_to_docx_bytes

st.set_page_config(
    page_title="SD Solutions (SDS)",
    page_icon="⚖️",
    layout="wide",
)

st.title("SD Solutions")
st.caption("SDS — evidence analysis, bulletproofing, and King's Counsel cross-examination prep")

st.warning(
    "Decision-support only. Not legal advice. "
    "Qualified legal counsel must review all outputs before court use.",
    icon="⚠️",
)

with st.sidebar:
    st.header("Case details")
    case_reference = st.text_input("Case / OC reference", value="CR-2026-001")
    st.markdown(
        "**Supported uploads:** `.txt`, `.md`, `.pdf`, `.docx`  \n"
        "**Security:** Prefer offline/on-prem deployment for live case material."
    )

uploaded = st.file_uploader(
    "Upload case documents",
    type=["txt", "md", "pdf", "docx"],
    accept_multiple_files=True,
)

run_demo = st.button("Run demo case (synthetic data)")

documents: dict[str, str] = {}

if run_demo:
    from sds.cli import _demo_documents

    documents = _demo_documents()

if uploaded:
    for file in uploaded:
        temp_path = Path("_upload_" + file.name)
        temp_path.write_bytes(file.getvalue())
        try:
            documents[file.name] = extract_text(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

if documents:
    report = analyze_case(documents, case_reference=case_reference)

    col1, col2, col3 = st.columns(3)
    col1.metric("Readiness score", f"{report.readiness_score}/100")
    col2.metric("Strengths", len(report.strengths))
    col3.metric("Weaknesses / gaps", len(report.weaknesses))

    st.info(report.summary)

    tab_docs, tab_strengths, tab_weaknesses, tab_actions, tab_xexam, tab_export = st.tabs(
        [
            "Documents",
            "Strengths",
            "Weaknesses",
            "Bulletproofing",
            "KC cross-examination",
            "Export",
        ]
    )

    with tab_docs:
        for doc in report.documents:
            st.markdown(f"**{doc.filename}** — {doc.word_count} words")
            st.write("Detected types: " + ", ".join(doc.detected_types))

    with tab_strengths:
        for item in report.strengths:
            st.success(f"**{item.title}** ({item.category}) — {item.detail}")

    with tab_weaknesses:
        for item in report.weaknesses:
            st.error(
                f"**[{item.severity.value.upper()}] {item.title}** "
                f"({item.category}) — {item.detail}"
            )

    with tab_actions:
        for rec in report.recommendations:
            st.markdown(
                f"{rec.priority}. **{rec.action}**  \n"
                f"_{rec.rationale}_  \n"
                f"Legal anchor: {rec.legal_anchor}"
            )

    with tab_xexam:
        st.markdown(
            "These questions simulate how senior criminal counsel may test the evidence. "
            "Use them in case conferences to close gaps **before** trial."
        )
        for idx, q in enumerate(report.cross_examination, 1):
            with st.expander(f"{idx}. {q.theme} — {q.target_witness}"):
                st.markdown(f"**Question:** {q.question}")
                st.markdown(f"**Purpose:** {q.purpose}")
                st.markdown(f"**Follow-up:** {q.follow_up}")

    with tab_export:
        markdown = report_to_markdown(report)
        docx_bytes = report_to_docx_bytes(report)
        st.download_button(
            "Download Word report (.docx)",
            data=docx_bytes,
            file_name=f"{case_reference}-sds-report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        st.text_area("Preview", markdown, height=400)

else:
    st.info("Upload documents or click **Run demo case** to begin.")

st.caption("SD Solutions (SDS) — decision-support only; not legal advice.")

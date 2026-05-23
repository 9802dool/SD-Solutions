# SD Solutions (SDS) — User Guide

Evidence and case-document analysis for Trinidad and Tobago criminal procedure contexts.

## What SDS does

1. **Upload** case documents (statements, scene notes, exhibit lists, forensic reports, disclosure schedules).
2. **Analyse** the bundle for strength and weakness signals (Evidence Act, disclosure, identification, digital integrity, etc.).
3. **Recommend** bulletproofing actions to close gaps before trial.
4. **Generate** anticipated King's Counsel-style cross-examination questions for case conferences.

## CLI

```powershell
cd "c:\Users\Simeon\OneDrive\Documents\SD-Solutions"
python -m sds --demo
python -m sds --case "OC-2026-0142" ".\path\to\file.txt"
python -m sds --demo --output ".\report.md"
```

## Web UI

```powershell
pip install -r requirements.txt
streamlit run sds/app.py
```

## King's Counsel pattern

Cross-examination templates follow senior criminal counsel techniques used in Commonwealth jurisdictions (including T&T):

| Theme | Example attack line |
|-------|---------------------|
| Statement fairness | Caution, recording, and Judges Rules compliance |
| Chain of custody | Seals, signatures, property-room continuity |
| Identification | Turnbull-style reliability |
| Digital evidence | Hash, forensic image, examiner statement |
| Hearsay | Document maker, originals, certificates |
| Disclosure | Late or unused material |
| Expert evidence | Qualifications, methodology, contamination |

## Security

Prefer offline or on-prem deployment for live case material. Do not upload sensitive files to public cloud without authorisation.

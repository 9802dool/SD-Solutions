# Trinidad & Tobago Legal Knowledge Base

SDS stores T&T law summaries in a SQLite database and exports them for the web app to cross-reference during evidence analysis.

## Initialise (seed TT laws)

```powershell
cd "C:\Users\Simeon\OneDrive\Documents\SD-Solutions"
python -m legal_kb init
```

This creates:
- `data/legal/tt_legal.db` — SQLite database
- `web/public/legal/kb.json` — exported for the website

## Upload new laws

Create a markdown file with sections:

```markdown
## s5-hearsay | Hearsay rule

Summary text here…
```

Import:

```powershell
python -m legal_kb import "C:\path\to\evidence-act-notes.md" --citation "Chap 7:02" --title "Evidence Act"
python -m legal_kb export
```

## Search and list

```powershell
python -m legal_kb list
python -m legal_kb list --citation "Chap 7:02"
python -m legal_kb search hearsay
```

## How cross-reference works

When SDS analyses a case file, it matches:
- Evidence weakness categories (hearsay, identification, disclosure, etc.)
- NLP triggers in the case text (DNA, CCTV, caution, etc.)
- Missing conviction elements

…to tagged sections in the legal KB and shows them in the **TT law refs** tab.

## Important

- Store **summaries and citations**, not full copyrighted statute text unless you have rights to reproduce them.
- Verify all entries against official sources (Judiciary, Parliament, Gazette).
- SDS legal cross-references are **not legal advice**.

## Web

Browse the library at `/legal` on the deployed site.

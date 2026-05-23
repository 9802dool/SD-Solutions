# SDS Architecture

SD Solutions combines **rule-based legal evaluation** with **NLP feature extraction** and **machine-learning conviction confidence** — always with mandatory human oversight.

## Layers

```
┌─────────────────────────────────────────────────────────┐
│  Input: PDF / TXT / DOCX police reports & evidence      │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  NLP feature extraction (features.py)                   │
│  Eyewitnesses, ID quality, DNA, CCTV, confession, etc.  │
└───────────────────────────┬─────────────────────────────┘
                            ▼
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
┌───────────────────┐                 ┌───────────────────┐
│ Rule engine       │                 │ Weighted scoring  │
│ (evidence_rules)  │                 │ (scoring.py)      │
│ Strengths/weakness│                 │ DNA high weight   │
└─────────┬─────────┘                 └─────────┬─────────┘
          │                                     │
          └──────────────────┬──────────────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Random Forest ML    │
                  │ (ml_model.py)       │
                  │ Conviction % output │
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Output              │
                  │ • Confidence %      │
                  │ • Conviction gaps   │
                  │ • Bulletproofing    │
                  │ • KC cross-exam     │
                  └─────────────────────┘
```

## Tech stack

| Component | Tool |
|-----------|------|
| Language | Python 3 (CLI/desktop), TypeScript (web) |
| NLP | Regex + entity patterns (spaCy optional future) |
| ML | scikit-learn Random Forest |
| Data | Pandas CSV training sets |
| Web | Next.js on Vercel (browser-only analysis) |

## Train the model

```powershell
cd SD-Solutions
pip install -r requirements.txt
python -m sds.train_model
```

Replace `data/training_cases.csv` with audited historical outcomes (Harvard Dataverse, NACJD, etc.) before operational use.

## Bias & human oversight

- Never use protected characteristics as features.
- Audit training data for neighbourhood/demographic bias.
- ML output is **supportive only** — not a charging or conviction decision.

from __future__ import annotations

import json
from pathlib import Path

from .features import FEATURE_NAMES, FeatureVector

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_PATH = MODEL_DIR / "case_strength_model.joblib"
WEIGHTS_JSON = MODEL_DIR / "feature_weights.json"

BIAS_NOTICE = (
    "Historical crime datasets may reflect systemic bias in policing and prosecution. "
    "SDS models must be audited for fairness before operational use and must never "
    "consider protected characteristics (race, religion, neighbourhood proxies, etc.). "
    "Predictions are supportive analytics only — not legal judgments."
)


def _confidence_label(probability: float) -> str:
    pct = probability * 100
    if pct >= 75:
        return f"{pct:.0f}% Strong"
    if pct >= 50:
        return f"{pct:.0f}% Developing"
    return f"{pct:.0f}% At risk"


def _heuristic_probability(vector: FeatureVector) -> float:
    """Fallback logistic-style score when sklearn model is unavailable."""
    weights = {
        "forensic_dna": 0.18,
        "forensic_fingerprint": 0.14,
        "confession_recorded": 0.12,
        "cctv_present": 0.10,
        "credible_eyewitnesses": 0.08,
        "identification_quality": 0.08,
        "weapon_recovered": 0.07,
        "expert_forensic": 0.07,
        "chain_of_custody": 0.06,
        "statement_quality": 0.05,
        "disclosure_complete": 0.04,
        "time_to_arrest_score": 0.03,
        "hearsay_risk": -0.12,
    }
    features = vector.as_dict()
    z = -0.5
    for key, w in weights.items():
        val = features[key]
        if key == "credible_eyewitnesses":
            val = min(1.0, val / 3.0)
        z += w * val
    # logistic
    import math

    prob = 1 / (1 + math.exp(-5 * z))
    return max(0.05, min(0.95, prob))


def predict_conviction_strength(vector: FeatureVector):
    from .models import ModelPrediction

    model_name = "heuristic-logistic-v1"
    probability = _heuristic_probability(vector)

    if MODEL_PATH.exists():
        try:
            import joblib  # type: ignore
            import pandas as pd  # type: ignore

            model = joblib.load(MODEL_PATH)
            frame = pd.DataFrame([vector.as_dict()])
            probability = float(model.predict_proba(frame)[0][1])
            model_name = "random-forest-v1"
        except Exception:
            pass

    return ModelPrediction(
        conviction_probability=round(probability, 3),
        confidence_label=_confidence_label(probability),
        model_name=model_name,
        human_oversight_required=True,
    )


def train_and_save_model(csv_path: Path | None = None) -> dict[str, float]:
    """Train Random Forest on historical-style features; export model + web weights."""
    import pandas as pd  # type: ignore
    from sklearn.ensemble import RandomForestClassifier  # type: ignore
    from sklearn.metrics import accuracy_score, f1_score  # type: ignore
    from sklearn.model_selection import train_test_split  # type: ignore
    import joblib  # type: ignore

    path = csv_path or Path(__file__).resolve().parents[1] / "data" / "training_cases.csv"
    df = pd.read_csv(path)
    x = df[FEATURE_NAMES]
    y = df["outcome"]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42)
    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(x_train, y_train)

    preds = model.predict(x_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, preds)),
        "f1": float(f1_score(y_test, preds)),
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    importances = dict(zip(FEATURE_NAMES, model.feature_importances_.tolist(), strict=True))
    WEIGHTS_JSON.write_text(json.dumps({"importances": importances, "metrics": metrics}, indent=2), encoding="utf-8")

    return metrics

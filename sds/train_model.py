#!/usr/bin/env python3
"""Train the SDS Random Forest case-strength model on historical-style data."""

from __future__ import annotations

import argparse
from pathlib import Path

from .ml_model import BIAS_NOTICE, train_and_save_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Train SDS Random Forest classifier.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Path to training CSV (default: data/training_cases.csv)",
    )
    args = parser.parse_args()

    metrics = train_and_save_model(args.csv)
    print("Model trained and saved to models/case_strength_model.joblib")
    print(f"Validation accuracy: {metrics['accuracy']:.2f}")
    print(f"Validation F1-score: {metrics['f1']:.2f}")
    print(f"\n{BIAS_NOTICE}")


if __name__ == "__main__":
    main()

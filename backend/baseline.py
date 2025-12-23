from __future__ import annotations
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression
import joblib

MODEL_PATH = Path(__file__).parent / "model.pkl"


FEATURES = [
    "gross_margin",
    "operating_margin",
    "net_margin",
    "debt_to_assets",
    "debt_to_equity",
    "receivables_turnover",
    "inventory_turnover",
    "cash_to_revenue",
    "current_assets_to_liabilities",
]


def _generate_synthetic(n: int = 500) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    gross = rng.normal(0.35, 0.12, n).clip(0, 0.8)
    op = rng.normal(0.15, 0.08, n).clip(-0.2, 0.5)
    net = rng.normal(0.10, 0.07, n).clip(-0.3, 0.4)
    dta = rng.normal(0.55, 0.2, n).clip(0.0, 1.5)
    dte = rng.normal(1.2, 0.8, n).clip(0.0, 5.0)
    rt = rng.normal(6.0, 3.0, n).clip(0.1, 20)
    it = rng.normal(4.0, 2.5, n).clip(0.1, 20)
    ctr = rng.normal(0.12, 0.08, n).clip(0.0, 0.6)
    cal = rng.normal(0.9, 0.6, n).clip(0.0, 3.0)

    X = np.vstack([gross, op, net, dta, dte, rt, it, ctr, cal]).T

    # Rule for label: good margins & moderate leverage -> up; poor margins or high leverage -> down; else flat
    y = np.zeros(n, dtype=int)  # 0=down,1=flat,2=up
    y[(gross > 0.4) & (net > 0.15) & (dta < 0.6)] = 2
    y[(gross < 0.2) | (net < 0.05) | (dta > 0.8)] = 0
    mask_flat = (y == 0) | (y == 2)
    # remaining default flat

    # Convert to binary for logistic regression: up vs not-up (simple baseline)
    y_bin = (y == 2).astype(int)
    return X, y_bin


def train_and_save() -> None:
    X, y = _generate_synthetic()
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X, y)
    joblib.dump(clf, MODEL_PATH)


def _ensure_model():
    if not MODEL_PATH.exists():
        train_and_save()


def predict(ratios: Dict[str, float]) -> Dict[str, object]:
    _ensure_model()
    clf: LogisticRegression = joblib.load(MODEL_PATH)
    x = np.array([[float(ratios.get(f, 0.0)) for f in FEATURES]])
    proba_up = float(clf.predict_proba(x)[0][1])
    # Map to direction categories
    if proba_up >= 0.6:
        direction = "up"
    elif proba_up <= 0.4:
        direction = "down"
    else:
        direction = "flat"
    return {"direction": direction, "score": proba_up}

"""
Unit tests for models.py and saved attack model artifacts.
Verifies:
1. Top-K accuracy calculation correctness.
2. Calibration curve outputs.
3. Per-region evaluation calculations.
4. Serialized artifacts (metrics.json and attack_model.joblib) are present and valid.
5. End-to-end model inference on test vectors.
"""

import json

import joblib
import numpy as np
import pandas as pd

from src.config import METRICS_JSON_PATH, MODELS_DIR
from src.models import (
    compute_calibration_curves,
    compute_per_region_metrics,
    compute_top_k_accuracy,
)


def test_compute_top_k_accuracy():
    """Verify top-k accuracy calculation."""
    classes = ["A", "B", "C", "D"]
    y_true = np.array(["A", "C", "D"])
    # Predictions:
    # row 0: ranks A (1st), B, C, D -> Hit at top-1
    # row 1: ranks B (1st), C (2nd), A, D -> Hit at top-2
    # row 2: ranks A (1st), B (2nd), C (3rd), D (4th) -> Miss at top-2, Hit at top-4
    y_proba = np.array([
        [0.7, 0.1, 0.1, 0.1],
        [0.2, 0.5, 0.3, 0.0],
        [0.4, 0.3, 0.2, 0.1],
    ])

    # Top-1 accuracy: row 0 hits, row 1 misses (pred B != C), row 2 misses (pred A != D) -> 1/3 ~ 0.3333
    acc_1 = compute_top_k_accuracy(y_true, y_proba, classes, k=1)
    assert acc_1 == 0.3333

    # Top-2 accuracy: row 0 hits, row 1 hits (C is 2nd), row 2 misses -> 2/3 ~ 0.6667
    acc_2 = compute_top_k_accuracy(y_true, y_proba, classes, k=2)
    assert acc_2 == 0.6667

    # Top-4 accuracy: all hit -> 3/3 = 1.0
    acc_4 = compute_top_k_accuracy(y_true, y_proba, classes, k=4)
    assert acc_4 == 1.0


def test_compute_calibration_curves():
    """Verify calibration curve generation structure."""
    classes = ["Bombing", "Assault"]
    y_true = np.array(["Bombing", "Bombing", "Assault", "Assault", "Bombing", "Assault"])
    y_proba = np.array([
        [0.8, 0.2],
        [0.9, 0.1],
        [0.2, 0.8],
        [0.3, 0.7],
        [0.7, 0.3],
        [0.1, 0.9],
    ])
    calib = compute_calibration_curves(y_true, y_proba, classes, n_bins=3)

    assert "Bombing" in calib
    assert "prob_pred" in calib["Bombing"]
    assert "prob_true" in calib["Bombing"]


def test_compute_per_region_metrics():
    """Verify per-region macro-F1 calculation."""
    y_true = ["A", "B", "A", "B"]
    y_pred = ["A", "B", "B", "A"]
    regions = ["Region 1", "Region 1", "Region 2", "Region 2"]

    reg_scores = compute_per_region_metrics(y_true, y_pred, regions)
    assert "Region 1" in reg_scores
    assert "Region 2" in reg_scores
    assert reg_scores["Region 1"]["macro_f1"] == 1.0  # Perfect predictions in Region 1


def test_saved_artifacts_validity():
    """Verify metrics.json exists, parses, and contains required candidate models."""
    assert METRICS_JSON_PATH.exists()
    with open(METRICS_JSON_PATH, "r") as f:
        metrics = json.load(f)

    assert "metadata" in metrics
    assert "models" in metrics
    assert "LightGBM" in metrics["models"]
    assert "Random Forest" in metrics["models"]
    assert "Logistic Regression" in metrics["models"]
    assert "Baseline (Majority Class)" in metrics["models"]


def test_saved_model_inference():
    """Verify saved champion model pipeline loads and executes inference."""
    model_path = MODELS_DIR / "attack_model.joblib"
    assert model_path.exists()

    payload = joblib.load(model_path)
    pipeline = payload["pipeline"]
    classes = payload["classes"]

    # Sample input
    sample_df = pd.DataFrame({
        "iyear": [2016],
        "region_txt": ["Middle East & North Africa"],
        "country_txt": ["Iraq"],
        "provstate": ["Baghdad"],
        "targtype1_txt": ["Military"],
        "weaptype1_txt": ["Explosives"],
        "gname": ["Unknown"],
        "latitude": [33.3152],
        "longitude": [44.3661],
        "coord_missing": [0],
    })

    probs = pipeline.predict_proba(sample_df)
    assert probs.shape == (1, len(classes))
    # Probabilities must sum to 1.0
    assert abs(probs[0].sum() - 1.0) < 1e-4

    pred = pipeline.predict(sample_df)
    assert pred[0] in classes

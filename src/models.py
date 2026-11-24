"""
Modeling, training, and multi-metric evaluation module for pre-attack classification.
Evaluates:
- Majority-class baseline
- Multinomial Logistic Regression
- Balanced Random Forest
- Class-weighted LightGBM / CatBoost
Calculates Accuracy, Macro-F1, Weighted-F1, Top-3 Accuracy, Per-class Precision/Recall,
Confusion Matrices, Calibration Curves (Reliability Diagrams), and Per-Region Macro-F1.
"""

import logging
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.calibration import calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from src.config import RANDOM_SEED

logger = logging.getLogger(__name__)


def compute_top_k_accuracy(
    y_true: Union[np.ndarray, pd.Series],
    y_proba: np.ndarray,
    classes: List[str],
    k: int = 3,
) -> float:
    """
    Compute Top-K accuracy: checks whether the true label is among the top K predicted probabilities.

    Parameters
    ----------
    y_true : array-like of shape (N,)
        True class labels.
    y_proba : ndarray of shape (N, n_classes)
        Predicted class probability matrix.
    classes : list of str
        List of class label names matching probability columns.
    k : int
        Top k ranks to evaluate (default: 3).

    Returns
    -------
    float
        Top-K accuracy bounded in [0.0, 1.0].
    """
    y_true_arr = np.asarray(y_true)
    class_to_idx = {c: i for i, c in enumerate(classes)}

    # Map true labels to indices
    true_indices = np.array([class_to_idx.get(label, -1) for label in y_true_arr])

    # Rank classes per sample (highest probability first)
    top_k_preds = np.argsort(y_proba, axis=1)[:, ::-1][:, :k]

    hits = 0
    for idx, true_idx in enumerate(true_indices):
        if true_idx in top_k_preds[idx]:
            hits += 1

    return round(float(hits / len(y_true_arr)), 4) if len(y_true_arr) > 0 else 0.0


def compute_calibration_curves(
    y_true: Union[np.ndarray, pd.Series],
    y_proba: np.ndarray,
    classes: List[str],
    n_bins: int = 5,
) -> Dict[str, Dict[str, List[float]]]:
    """
    Compute reliability diagram coordinates (mean predicted probability vs fraction of positives)
    for each class in a one-vs-rest configuration.

    Parameters
    ----------
    y_true : array-like
        True class labels.
    y_proba : ndarray of shape (N, n_classes)
        Predicted class probabilities.
    classes : list of str
        Class labels.
    n_bins : int
        Number of probability discretization bins.

    Returns
    -------
    dict
        Dictionary mapping class_name -> {'prob_true': [...], 'prob_pred': [...]}
    """
    y_true_arr = np.asarray(y_true)
    calibration_data: Dict[str, Dict[str, List[float]]] = {}

    for idx, cname in enumerate(classes):
        # Binary target for this class
        y_binary = (y_true_arr == cname).astype(int)
        c_proba = y_proba[:, idx]

        if len(np.unique(y_binary)) > 1:
            try:
                prob_true, prob_pred = calibration_curve(
                    y_binary,
                    c_proba,
                    n_bins=n_bins,
                    strategy="uniform",
                )
                calibration_data[cname] = {
                    "prob_true": [round(float(p), 4) for p in prob_true],
                    "prob_pred": [round(float(p), 4) for p in prob_pred],
                }
            except Exception as e:
                logger.warning("Calibration calculation failed for %s: %e", cname, e)
                calibration_data[cname] = {"prob_true": [], "prob_pred": []}
        else:
            calibration_data[cname] = {"prob_true": [], "prob_pred": []}

    return calibration_data


def compute_per_region_metrics(
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series],
    regions: Union[np.ndarray, pd.Series],
) -> Dict[str, Dict[str, float]]:
    """
    Compute Macro-F1 and sample count for each geographic region.

    Parameters
    ----------
    y_true : array-like
        True labels.
    y_pred : array-like
        Predicted labels.
    regions : array-like
        Geographic region labels.

    Returns
    -------
    dict
        Region name -> {'macro_f1': float, 'count': int}
    """
    df_eval = pd.DataFrame({
        "true": np.asarray(y_true),
        "pred": np.asarray(y_pred),
        "region": np.asarray(regions),
    })

    region_scores: Dict[str, Dict[str, float]] = {}
    for rname, group in df_eval.groupby("region"):
        if len(group) == 0:
            continue
        score = f1_score(group["true"], group["pred"], average="macro", zero_division=0)
        region_scores[str(rname)] = {
            "macro_f1": round(float(score), 4),
            "sample_count": int(len(group)),
        }

    return region_scores


def evaluate_model(
    model_name: str,
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series],
    y_proba: np.ndarray,
    classes: List[str],
    regions: Optional[Union[np.ndarray, pd.Series]] = None,
) -> Dict[str, Any]:
    """
    Generate complete evaluation profile for a model.

    Returns
    -------
    dict
        Comprehensive metrics dictionary suitable for serialization to artifacts/metrics.json.
    """
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    top3_acc = compute_top_k_accuracy(y_true, y_proba, classes, k=min(3, len(classes)))

    # Per-class metrics
    p, r, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=classes, zero_division=0
    )
    per_class = {}
    for i, cname in enumerate(classes):
        per_class[cname] = {
            "precision": round(float(p[i]), 4),
            "recall": round(float(r[i]), 4),
            "f1_score": round(float(f1[i]), 4),
            "support": int(support[i]),
        }

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=classes)

    # Calibration curves
    calib = compute_calibration_curves(y_true, y_proba, classes, n_bins=5)

    # Region breakdown
    reg_scores = compute_per_region_metrics(y_true, y_pred, regions) if regions is not None else {}

    return {
        "model_name": model_name,
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "top3_accuracy": round(float(top3_acc), 4),
        "classes": classes,
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
        "calibration_curves": calib,
        "per_region_macro_f1": reg_scores,
    }


def get_candidate_models(random_seed: int = RANDOM_SEED) -> Dict[str, Any]:
    """
    Initialize candidate classifiers with class weights and balanced parameters:
    1. Majority-class baseline
    2. Multinomial Logistic Regression (balanced)
    3. Balanced Random Forest
    4. Balanced LightGBM
    """
    models = {
        "Baseline (Majority Class)": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(
            class_weight="balanced",
            max_iter=500,
            random_state=random_seed,
            solver="saga",
            n_jobs=-1,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            class_weight="balanced",
            max_depth=12,
            random_state=random_seed,
            n_jobs=-1,
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=120,
            class_weight="balanced",
            learning_rate=0.08,
            max_depth=6,
            num_leaves=31,
            random_state=random_seed,
            verbosity=-1,
            n_jobs=-1,
        ),
    }
    return models

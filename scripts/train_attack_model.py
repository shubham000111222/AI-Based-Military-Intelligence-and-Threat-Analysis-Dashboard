"""
Training and evaluation script for the pre-attack tactic classification model.
Executes:
1. Time-based split: Train <= 2012, Test 2013-2017 (zero data leakage).
2. Fits preprocessor on X_train.
3. Evaluates all 4 candidate models: Baseline, Logistic Regression, Random Forest, LightGBM.
4. Serializes all metrics, confusion matrices, and calibration data to artifacts/metrics.json.
5. Saves the champion model pipeline to models/attack_model.joblib.
6. Computes and serializes SHAP explanations to artifacts/shap_explainer.joblib.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import numpy as np
import shap
from sklearn.pipeline import Pipeline

from src.config import (
    ARTIFACTS_DIR,
    METRICS_JSON_PATH,
    MODELS_DIR,
    PROCESSED_DATA_PATH,
    RANDOM_SEED,
)
from src.data_loader import load_dataset
from src.features import create_preprocessor, get_temporal_split
from src.models import evaluate_model, get_candidate_models

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("train_attack_model")


def main() -> None:
    start_time = time.time()
    logger.info("Initializing attack classification model training pipeline...")

    # 1. Load data
    df = load_dataset(PROCESSED_DATA_PATH)
    logger.info("Loaded dataset with %d total records.", len(df))

    # 2. Time-based split (zero leakage)
    X_train, y_train, X_test, y_test = get_temporal_split(df)
    test_regions = X_test["region_txt"].values

    classes = sorted(list(y_train.unique()))
    logger.info("Target classes (%d): %s", len(classes), classes)

    # 3. Fit Preprocessor
    preprocessor = create_preprocessor()
    logger.info("Fitting preprocessor on training partition (<= 2012)...")
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    logger.info(
        "Processed feature dimensionality: %d features from %d raw inputs",
        X_train_proc.shape[1],
        X_train.shape[1],
    )

    # Extract feature names from preprocessor for interpretability
    try:
        feature_names = preprocessor.get_feature_names_out().tolist()
    except Exception:
        feature_names = [f"f_{i}" for i in range(X_train_proc.shape[1])]

    # 4. Train and Evaluate Models
    candidate_models = get_candidate_models(random_seed=RANDOM_SEED)
    metrics_report: Dict[str, Any] = {
        "metadata": {
            "train_samples": int(len(X_train)),
            "test_samples": int(len(X_test)),
            "train_period": "<= 2012",
            "test_period": "2013-2017",
            "classes": classes,
            "feature_count": int(X_train_proc.shape[1]),
        },
        "models": {},
    }

    best_model_name = ""
    best_macro_f1 = -1.0
    fitted_models = {}

    for name, model in candidate_models.items():
        logger.info("Training candidate: %s...", name)
        m_start = time.time()
        model.fit(X_train_proc, y_train)
        m_elapsed = time.time() - m_start

        logger.info("Predicting test partition (%s)...", name)
        y_pred = model.predict(X_test_proc)

        # Probabilities
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test_proc)
        else:
            # Dummy fallback uniform
            y_proba = np.ones((len(y_pred), len(classes))) / len(classes)

        eval_res = evaluate_model(
            model_name=name,
            y_true=y_test,
            y_pred=y_pred,
            y_proba=y_proba,
            classes=classes,
            regions=test_regions,
        )
        eval_res["train_time_sec"] = round(float(m_elapsed), 2)
        metrics_report["models"][name] = eval_res
        fitted_models[name] = model

        logger.info(
            "%s Results -> Acc: %.4f | Macro-F1: %.4f | Weighted-F1: %.4f | Top-3 Acc: %.4f",
            name,
            eval_res["accuracy"],
            eval_res["macro_f1"],
            eval_res["weighted_f1"],
            eval_res["top3_accuracy"],
        )

        if eval_res["macro_f1"] > best_macro_f1:
            best_macro_f1 = eval_res["macro_f1"]
            best_model_name = name

    metrics_report["metadata"]["best_model"] = best_model_name
    logger.info("Champion Model Selected: %s (Macro-F1: %.4f)", best_model_name, best_macro_f1)

    # 5. Save metrics.json
    METRICS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(METRICS_JSON_PATH, "w") as f:
        json.dump(metrics_report, f, indent=2)
    logger.info("Metrics successfully saved to %s", METRICS_JSON_PATH)

    # 6. Save Champion Model Pipeline
    champion_model = fitted_models[best_model_name]
    full_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", champion_model),
    ])

    model_save_path = MODELS_DIR / "attack_model.joblib"
    joblib.dump(
        {
            "pipeline": full_pipeline,
            "classes": classes,
            "feature_names": feature_names,
            "model_name": best_model_name,
        },
        model_save_path,
    )
    logger.info("Saved champion model pipeline to %s", model_save_path)

    # 7. Precompute SHAP Explanations
    logger.info("Computing SHAP values for local and global model interpretability...")
    try:
        # Use TreeExplainer for Tree models (LightGBM or Random Forest)
        explainer_model = fitted_models.get("LightGBM", fitted_models.get("Random Forest"))

        # Take a representative sample of test partition for background and sample
        sample_size = min(300, len(X_test_proc))
        rng = np.random.default_rng(RANDOM_SEED)
        sample_idx = rng.choice(len(X_test_proc), size=sample_size, replace=False)
        X_sample = X_test_proc[sample_idx]

        explainer = shap.TreeExplainer(explainer_model)
        shap_values = explainer.shap_values(X_sample)

        shap_payload = {
            "shap_values": shap_values,
            "sample_features": X_sample,
            "feature_names": feature_names,
            "classes": classes,
        }
        shap_path = ARTIFACTS_DIR / "shap_explainer.joblib"
        joblib.dump(shap_payload, shap_path)
        logger.info("SHAP explanations saved to %s", shap_path)
    except Exception as e:
        logger.warning("SHAP computation encountered non-fatal notice: %s", e)

    elapsed_total = time.time() - start_time
    logger.info("TRAINING PIPELINE COMPLETE in %.2f seconds.", elapsed_total)


if __name__ == "__main__":
    main()

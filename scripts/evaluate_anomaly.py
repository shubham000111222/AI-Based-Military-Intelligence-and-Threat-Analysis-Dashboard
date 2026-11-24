"""
Evaluation script for early-warning anomaly and tactical surge detection.
Builds monthly panel dataset, computes rolling statistics and forward surge ground-truth labels,
fits Rolling Z-Score and Isolation Forest detectors, evaluates precision/recall/F1/lead time
on the 2013-2017 out-of-time window, and saves metrics to artifacts/anomaly_eval.json.
Also saves precomputed panel alerts to artifacts/anomaly_alerts.parquet for rapid UI loading.
"""

import json
import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.anomaly import (
    build_monthly_country_series,
    compute_early_warning_features,
    evaluate_early_warning_backtest,
    fit_and_detect_anomalies,
)
from src.config import ARTIFACTS_DIR, PROCESSED_DATA_PATH
from src.data_loader import load_dataset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("evaluate_anomaly")


def main() -> None:
    start_time = time.time()
    logger.info("Initializing early-warning anomaly detection pipeline...")

    # 1. Load data
    df = load_dataset(PROCESSED_DATA_PATH)

    # 2. Build monthly country panel (top 50 countries)
    logger.info("Building continuous monthly panel for top sovereign states...")
    panel_df = build_monthly_country_series(df, top_n_countries=50)

    # 3. Compute early warning features and forward surge labels
    logger.info("Computing rolling 12m statistics and forward 3-month surge labels...")
    features_df = compute_early_warning_features(panel_df)

    # 4. Fit dual detectors (Rolling Z-Score & Isolation Forest)
    logger.info("Fitting unsupervised Isolation Forest and Rolling Z-Score detectors...")
    alerts_df = fit_and_detect_anomalies(features_df, z_threshold=2.0, contamination=0.05)

    # 5. Out-of-time Backtest Evaluation (2013-2017)
    logger.info("Executing 2013-2017 out-of-time surge prediction benchmark...")
    eval_report = evaluate_early_warning_backtest(alerts_df)

    # 6. Save metrics to artifacts/anomaly_eval.json
    output_json = ARTIFACTS_DIR / "anomaly_eval.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w") as f:
        json.dump(eval_report, f, indent=2)
    logger.info("Evaluation report saved to %s", output_json)

    # 7. Save precomputed panel alerts to Parquet
    alerts_parquet = ARTIFACTS_DIR / "anomaly_alerts.parquet"
    alerts_df.to_parquet(alerts_parquet, index=False)
    logger.info("Panel alerts successfully saved to %s", alerts_parquet)

    elapsed = time.time() - start_time
    logger.info("ANOMALY PIPELINE COMPLETE in %.2f seconds.", elapsed)


if __name__ == "__main__":
    main()

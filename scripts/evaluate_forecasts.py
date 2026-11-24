"""
Evaluation script for longitudinal threat forecasting backtests.
Executes temporal out-of-time backtesting (Train <= 2012, Test 2013-2017) across:
- Global Total
- All major geographic theatres
Compares Holt-Winters Exponential Smoothing (ETS) against Naive and Moving Average baselines.
Saves comprehensive results to artifacts/forecast_eval.json.
"""

import json
import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import ARTIFACTS_DIR, PROCESSED_DATA_PATH
from src.data_loader import load_dataset
from src.forecasting import evaluate_forecast_backtest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("evaluate_forecasts")


def main() -> None:
    start_time = time.time()
    logger.info("Initializing longitudinal threat forecasting backtest...")

    df = load_dataset(PROCESSED_DATA_PATH)

    regions_to_evaluate = [
        "Global Total",
        "Middle East & North Africa",
        "South Asia",
        "Sub-Saharan Africa",
        "Western Europe",
        "South America",
        "Southeast Asia",
        "North America",
        "Eastern Europe",
    ]

    all_results = {}

    for region in regions_to_evaluate:
        reg_arg = None if region == "Global Total" else region
        logger.info("Backtesting horizon 2013-2017 for theatre: %s...", region)
        try:
            res = evaluate_forecast_backtest(df, region=reg_arg)
            all_results[region] = res
            ets_mae = res["models"]["Holt-Winters ETS"]["mae"]
            ets_mape = res["models"]["Holt-Winters ETS"]["mape"]
            naive_mae = res["models"]["Naive (Last Value)"]["mae"]
            naive_mape = res["models"]["Naive (Last Value)"]["mape"]
            logger.info(
                "[%s] ETS MAE: %.1f (MAPE: %.1f%%) | Naive MAE: %.1f (MAPE: %.1f%%)",
                region,
                ets_mae,
                ets_mape,
                naive_mae,
                naive_mape,
            )
        except Exception as e:
            logger.warning("Backtest failed for region '%s': %s", region, e)

    output_path = ARTIFACTS_DIR / "forecast_eval.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    elapsed = time.time() - start_time
    logger.info("Backtest evaluation complete in %.2f seconds. Output saved to %s", elapsed, output_path)


if __name__ == "__main__":
    main()

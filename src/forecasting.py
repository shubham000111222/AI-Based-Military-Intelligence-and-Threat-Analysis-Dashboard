"""
Time-series forecasting module for incident volume with strict validation.
Supports:
- Naive Last-Value baseline
- 3-Year Moving Average baseline
- Holt-Winters Exponential Smoothing (ETS) with confidence bounds
- Temporal backtest validation (Train <= 2012, Forecast 2013-2017) with MAE & MAPE
- Ex-ante future projections with a strict 5-year maximum horizon constraint
- Explicit handling and interpolation flagging for the missing 1993 archival year.
"""

import logging
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.config import MISSING_YEAR, TRAIN_MAX_YEAR

logger = logging.getLogger(__name__)

# Maximum allowable horizon for conflict forecasting
MAX_FORECAST_HORIZON: int = 5
HORIZON_LIMIT_EXPLANATION: str = (
    "OPERATIONAL HORIZON LIMIT (MAX 5 YEARS): Statistical forecasting models cannot extrapolate "
    "beyond a 5-year horizon in political violence domains. Geopolitical structural breaks, emergence "
    "of novel militant factions, state counter-insurgency doctrine shifts, and compounding error variance "
    "render projections beyond 5 years scientifically invalid."
)


def extract_annual_series(
    df: pd.DataFrame,
    region: Optional[str] = None,
    interpolate_1993: bool = True,
) -> pd.DataFrame:
    """
    Extract annual incident frequency series with explicit 1993 gap handling.

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame.
    region : str, optional
        Geographic region filter. If None or 'All Regions', aggregates globally.
    interpolate_1993 : bool
        If True, linearly interpolates the missing 1993 value for statistical continuity,
        while maintaining an 'is_interpolated' boolean flag.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: ['iyear', 'incidents', 'is_interpolated']
    """
    sub = df.copy()
    if region is not None and region != "All Regions" and region != "Global Total":
        sub = sub[sub["region_txt"] == region]

    # Aggregate by year
    yearly_counts = sub.groupby("iyear").size().reset_index(name="incidents")

    # Complete sequence from min to max year
    min_yr = int(yearly_counts["iyear"].min()) if not yearly_counts.empty else 1970
    max_yr = int(yearly_counts["iyear"].max()) if not yearly_counts.empty else 2017
    full_years = pd.DataFrame({"iyear": list(range(min_yr, max_yr + 1))})

    merged = pd.merge(full_years, yearly_counts, on="iyear", how="left")
    merged["is_interpolated"] = False

    # Check for 1993
    if 1993 in merged["iyear"].values:
        idx_1993 = merged[merged["iyear"] == 1993].index[0]
        # In GTD 1993 is completely missing / NaN
        if pd.isna(merged.loc[idx_1993, "incidents"]) or merged.loc[idx_1993, "incidents"] == 0:
            if interpolate_1993:
                # Linear interpolation between 1992 and 1994
                val_1992 = merged.loc[merged["iyear"] == 1992, "incidents"].values
                val_1994 = merged.loc[merged["iyear"] == 1994, "incidents"].values
                v92 = val_1992[0] if len(val_1992) > 0 and not pd.isna(val_1992[0]) else 0
                v94 = val_1994[0] if len(val_1994) > 0 and not pd.isna(val_1994[0]) else 0
                merged.loc[idx_1993, "incidents"] = round((v92 + v94) / 2.0, 1)
                merged.loc[idx_1993, "is_interpolated"] = True
            else:
                merged.loc[idx_1993, "incidents"] = 0.0

    # Fill any remaining NaNs with 0
    merged["incidents"] = merged["incidents"].fillna(0.0)
    return merged.sort_values("iyear").reset_index(drop=True)


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    return round(float(np.mean(np.abs(y_true - y_pred))), 2)


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error (handles 0 division gracefully)."""
    mask = y_true > 0
    if not mask.any():
        return 0.0
    return round(float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100), 2)


def fit_naive_baseline(train_series: np.ndarray, horizon: int) -> np.ndarray:
    """
    Naive last-value benchmark: repeats the last observed incident count across horizon.
    """
    last_val = train_series[-1] if len(train_series) > 0 else 0.0
    return np.full(horizon, last_val, dtype=float)


def fit_moving_average_baseline(
    train_series: np.ndarray,
    horizon: int,
    window: int = 3,
) -> np.ndarray:
    """
    Moving average benchmark: projects the trailing k-year mean across horizon.
    """
    w = min(window, len(train_series))
    avg_val = np.mean(train_series[-w:]) if w > 0 else 0.0
    return np.full(horizon, round(float(avg_val), 1), dtype=float)


def fit_exponential_smoothing_forecast(
    train_series: np.ndarray,
    horizon: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Fit Holt-Winters Exponential Smoothing (ETS) with additive trend.
    Computes point forecast along with 80% and 95% confidence intervals based on residual variance.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        (point_forecast, lower_80, upper_80, lower_95, upper_95)
    """
    if len(train_series) < 4:
        # Fallback to naive if series is too short
        pt = fit_naive_baseline(train_series, horizon)
        return pt, pt * 0.8, pt * 1.2, pt * 0.6, pt * 1.4

    try:
        model = ExponentialSmoothing(
            train_series,
            trend="add",
            damped_trend=True,
            initialization_method="estimated",
        )
        fitted = model.fit(damping_trend=0.9)
        pred = fitted.forecast(horizon)
        pred = np.clip(pred, a_min=0.0, a_max=None)

        # Residual standard error
        residuals = fitted.resid
        sigma = np.std(residuals) if len(residuals) > 0 else 1.0

        # Horizon variance scaling: sqrt(h)
        h_steps = np.sqrt(np.arange(1, horizon + 1))
        z_80 = 1.282
        z_95 = 1.960

        lower_80 = np.clip(pred - z_80 * sigma * h_steps, a_min=0.0, a_max=None)
        upper_80 = pred + z_80 * sigma * h_steps
        lower_95 = np.clip(pred - z_95 * sigma * h_steps, a_min=0.0, a_max=None)
        upper_95 = pred + z_95 * sigma * h_steps

        return (
            np.round(pred, 1),
            np.round(lower_80, 1),
            np.round(upper_80, 1),
            np.round(lower_95, 1),
            np.round(upper_95, 1),
        )
    except Exception as e:
        logger.warning("ExponentialSmoothing fit failed: %s. Falling back to damped trend.", e)
        pt = fit_moving_average_baseline(train_series, horizon, window=3)
        return pt, pt * 0.85, pt * 1.15, pt * 0.70, pt * 1.30


def evaluate_forecast_backtest(
    df: pd.DataFrame,
    region: Optional[str] = None,
    train_end_year: int = TRAIN_MAX_YEAR,  # 2012
    test_end_year: int = 2017,
) -> Dict[str, Any]:
    """
    Execute out-of-time backtest by training through 2012 and forecasting 2013-2017.
    Compares Exponential Smoothing (ETS) against Naive and 3-Year Moving Average baselines.

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame.
    region : str, optional
        Geographic theatre filter.
    train_end_year : int
        Cutoff year for training data (default: 2012).
    test_end_year : int
        Final year of test evaluation window (default: 2017).

    Returns
    -------
    dict
        Comprehensive backtest report containing MAE, MAPE, and predicted vs actual arrays.
    """
    ts_df = extract_annual_series(df, region=region, interpolate_1993=True)

    train_part = ts_df[ts_df["iyear"] <= train_end_year]
    test_part = ts_df[(ts_df["iyear"] > train_end_year) & (ts_df["iyear"] <= test_end_year)]

    y_train = train_part["incidents"].values
    y_test = test_part["incidents"].values
    test_years = test_part["iyear"].values.tolist()
    horizon = len(y_test)

    # 1. Naive
    naive_preds = fit_naive_baseline(y_train, horizon)
    naive_mae = calculate_mae(y_test, naive_preds)
    naive_mape = calculate_mape(y_test, naive_preds)

    # 2. Moving Average (3-Year)
    ma_preds = fit_moving_average_baseline(y_train, horizon, window=3)
    ma_mae = calculate_mae(y_test, ma_preds)
    ma_mape = calculate_mape(y_test, ma_preds)

    # 3. Exponential Smoothing (ETS)
    ets_preds, l80, u80, l95, u95 = fit_exponential_smoothing_forecast(y_train, horizon)
    ets_mae = calculate_mae(y_test, ets_preds)
    ets_mape = calculate_mape(y_test, ets_preds)

    return {
        "region": region if region else "Global Total",
        "train_period": f"{int(train_part['iyear'].min())}–{train_end_year}",
        "test_period": f"{train_end_year + 1}–{test_end_year}",
        "test_years": test_years,
        "actual_values": [round(float(v), 1) for v in y_test],
        "models": {
            "Naive (Last Value)": {
                "predictions": [round(float(v), 1) for v in naive_preds],
                "mae": naive_mae,
                "mape": naive_mape,
            },
            "Moving Average (3-Yr)": {
                "predictions": [round(float(v), 1) for v in ma_preds],
                "mae": ma_mae,
                "mape": ma_mape,
            },
            "Holt-Winters ETS": {
                "predictions": [round(float(v), 1) for v in ets_preds],
                "mae": ets_mae,
                "mape": ets_mape,
                "lower_80": [round(float(v), 1) for v in l80],
                "upper_80": [round(float(v), 1) for v in u80],
                "lower_95": [round(float(v), 1) for v in l95],
                "upper_95": [round(float(v), 1) for v in u95],
            },
        },
    }


def generate_future_forecast(
    df: pd.DataFrame,
    region: Optional[str] = None,
    horizon_years: int = 5,
) -> Dict[str, Any]:
    """
    Generate future ex-ante forecasts through 2017 + H (max H=5).

    Returns
    -------
    dict
        Point forecasts, confidence intervals, and operational limit notes.
    """
    # Enforce strict 5-year maximum horizon
    safe_horizon = min(max(int(horizon_years), 1), MAX_FORECAST_HORIZON)

    ts_df = extract_annual_series(df, region=region, interpolate_1993=True)
    full_y = ts_df["incidents"].values
    last_year = int(ts_df["iyear"].max())

    pred, l80, u80, l95, u95 = fit_exponential_smoothing_forecast(full_y, safe_horizon)
    future_years = [last_year + i for i in range(1, safe_horizon + 1)]

    return {
        "region": region if region else "Global Total",
        "historical_years": ts_df["iyear"].tolist(),
        "historical_incidents": ts_df["incidents"].tolist(),
        "is_interpolated_1993": bool(ts_df[ts_df["iyear"] == MISSING_YEAR]["is_interpolated"].iloc[0])
        if MISSING_YEAR in ts_df["iyear"].values else False,
        "forecast_years": future_years,
        "point_forecast": [round(float(v), 1) for v in pred],
        "lower_80": [round(float(v), 1) for v in l80],
        "upper_80": [round(float(v), 1) for v in u80],
        "lower_95": [round(float(v), 1) for v in l95],
        "upper_95": [round(float(v), 1) for v in u95],
        "horizon_limit_note": HORIZON_LIMIT_EXPLANATION,
    }

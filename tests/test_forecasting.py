"""
Unit tests for forecasting.py time series models and backtest validation.
"""

import numpy as np

from src.forecasting import (
    MAX_FORECAST_HORIZON,
    evaluate_forecast_backtest,
    extract_annual_series,
    fit_exponential_smoothing_forecast,
    fit_moving_average_baseline,
    fit_naive_baseline,
    generate_future_forecast,
)


def test_extract_annual_series_1993_gap_handling(synthetic_multidecade_df):
    """Verify 1993 gap interpolation and schema."""
    ts_df = extract_annual_series(synthetic_multidecade_df, interpolate_1993=True)

    assert "iyear" in ts_df.columns
    assert "incidents" in ts_df.columns
    assert "is_interpolated" in ts_df.columns

    # 1993 must be present and marked as interpolated
    row_1993 = ts_df[ts_df["iyear"] == 1993]
    assert len(row_1993) == 1
    assert bool(row_1993["is_interpolated"].iloc[0]) is True
    assert row_1993["incidents"].iloc[0] > 0


def test_fit_naive_baseline():
    """Verify naive last-value baseline projections."""
    train = np.array([10.0, 20.0, 30.0, 45.0])
    horizon = 4
    preds = fit_naive_baseline(train, horizon=horizon)

    assert len(preds) == horizon
    assert (preds == 45.0).all()


def test_fit_moving_average_baseline():
    """Verify 3-year moving average baseline projections."""
    train = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    horizon = 3
    preds = fit_moving_average_baseline(train, horizon=horizon, window=3)

    assert len(preds) == horizon
    # Mean of last 3: (30 + 40 + 50) / 3 = 40.0
    assert preds[0] == 40.0


def test_fit_exponential_smoothing_properties():
    """Verify Holt-Winters ETS point forecasts and confidence interval ordering."""
    train = np.array([100.0, 110.0, 125.0, 140.0, 160.0, 185.0, 210.0])
    horizon = 5

    pred, l80, u80, l95, u95 = fit_exponential_smoothing_forecast(train, horizon=horizon)

    assert len(pred) == horizon
    assert len(l80) == horizon
    assert len(u80) == horizon
    assert len(l95) == horizon
    assert len(u95) == horizon

    # Bounds hierarchy: l95 <= l80 <= pred <= u80 <= u95
    assert (l95 <= l80).all()
    assert (l80 <= pred).all()
    assert (pred <= u80).all()
    assert (u80 <= u95).all()

    # Non-negative
    assert (l95 >= 0.0).all()


def test_evaluate_forecast_backtest(synthetic_multidecade_df):
    """Verify temporal backtest evaluation output."""
    res = evaluate_forecast_backtest(synthetic_multidecade_df)

    assert "models" in res
    assert "Holt-Winters ETS" in res["models"]
    assert "Naive (Last Value)" in res["models"]
    assert "Moving Average (3-Yr)" in res["models"]

    ets_res = res["models"]["Holt-Winters ETS"]
    assert ets_res["mae"] >= 0.0
    assert ets_res["mape"] >= 0.0
    assert len(ets_res["predictions"]) == len(res["test_years"])


def test_generate_future_forecast_horizon_cap(synthetic_multidecade_df):
    """Verify forecast horizon is strictly capped at MAX_FORECAST_HORIZON (5 years)."""
    # Request 10 years
    fc = generate_future_forecast(synthetic_multidecade_df, horizon_years=10)

    # Must be capped at 5
    assert len(fc["forecast_years"]) == MAX_FORECAST_HORIZON
    assert len(fc["point_forecast"]) == MAX_FORECAST_HORIZON
    assert "horizon_limit_note" in fc

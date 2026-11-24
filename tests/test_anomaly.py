"""
Unit tests for anomaly.py early-warning surge detection and backtesting.
"""


from src.anomaly import (
    ANOMALY_DISCLAIMER,
    build_monthly_country_series,
    compute_early_warning_features,
    evaluate_early_warning_backtest,
    fit_and_detect_anomalies,
    get_top_recent_alerts,
)


def test_build_monthly_country_series(synthetic_multidecade_df):
    """Verify monthly continuous panel generation for top countries."""
    panel_df = build_monthly_country_series(synthetic_multidecade_df, top_n_countries=5)

    assert len(panel_df) > 0
    assert "country_txt" in panel_df.columns
    assert "year_month" in panel_df.columns
    assert "incident_count" in panel_df.columns
    assert "casualty_count" in panel_df.columns

    # No negative counts
    assert (panel_df["incident_count"] >= 0).all()
    assert (panel_df["casualty_count"] >= 0.0).all()


def test_compute_early_warning_features(synthetic_multidecade_df):
    """Verify 12m rolling features and surge binary labeling."""
    panel_df = build_monthly_country_series(synthetic_multidecade_df, top_n_countries=5)
    feat_df = compute_early_warning_features(panel_df)

    assert "rolling_mean_12m" in feat_df.columns
    assert "rolling_std_12m" in feat_df.columns
    assert "z_score" in feat_df.columns
    assert "is_surge" in feat_df.columns

    # is_surge must be binary (0 or 1)
    assert set(feat_df["is_surge"].unique()).issubset({0, 1})


def test_fit_and_detect_anomalies(synthetic_multidecade_df):
    """Verify dual anomaly detectors: Z-Score and Isolation Forest."""
    panel_df = build_monthly_country_series(synthetic_multidecade_df, top_n_countries=5)
    feat_df = compute_early_warning_features(panel_df)
    alert_df = fit_and_detect_anomalies(feat_df, z_threshold=2.0)

    assert "alert_zscore" in alert_df.columns
    assert "alert_iso" in alert_df.columns
    assert "composite_anomaly_score" in alert_df.columns

    assert set(alert_df["alert_zscore"].unique()).issubset({0, 1})
    assert set(alert_df["alert_iso"].unique()).issubset({0, 1})


def test_evaluate_early_warning_backtest(synthetic_multidecade_df):
    """Verify out-of-time backtest returns metrics for candidate detectors."""
    panel_df = build_monthly_country_series(synthetic_multidecade_df, top_n_countries=5)
    feat_df = compute_early_warning_features(panel_df)
    alert_df = fit_and_detect_anomalies(feat_df)

    report = evaluate_early_warning_backtest(alert_df, train_end_year=2012, test_start_year=2013, test_end_year=2017)

    assert "models" in report
    assert "Rolling Z-Score Detector (z >= 2.0)" in report["models"]
    assert "Isolation Forest Detector" in report["models"]
    assert "Fixed-Threshold Baseline (90th Pct)" in report["models"]

    z_model = report["models"]["Rolling Z-Score Detector (z >= 2.0)"]
    assert 0.0 <= z_model["precision"] <= 1.0
    assert 0.0 <= z_model["recall"] <= 1.0
    assert 0.0 <= z_model["f1_score"] <= 1.0
    assert z_model["average_lead_time_months"] > 0


def test_get_top_recent_alerts(synthetic_multidecade_df):
    """Verify top alerts table extraction."""
    panel_df = build_monthly_country_series(synthetic_multidecade_df, top_n_countries=5)
    feat_df = compute_early_warning_features(panel_df)
    alert_df = fit_and_detect_anomalies(feat_df)

    top_alerts = get_top_recent_alerts(alert_df, top_n=5)
    assert len(top_alerts) <= 5
    assert "Sovereign State" in top_alerts.columns
    assert "Threat Score" in top_alerts.columns
    assert "Detection Rationale" in top_alerts.columns


def test_anomaly_disclaimer_content():
    """Verify mandatory operational disclaimer exists."""
    assert "NOT predictions of specific kinetic operations" in ANOMALY_DISCLAIMER

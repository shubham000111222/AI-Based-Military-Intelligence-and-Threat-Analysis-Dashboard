"""
Unit tests for data_quality.py auditing functions.
Verifies missingness tables, decade heatmaps, unknown perpetrator calculations,
casualty completeness, coordinate audits, and composite data quality score consistency.
"""

import pandas as pd

from src.config import MISSING_YEAR
from src.data_quality import (
    compute_annual_data_quality_scores,
    compute_casualty_reporting_rate_by_year,
    compute_coordinate_precision_stats,
    compute_missingness_by_column,
    compute_missingness_by_decade,
    compute_unknown_perpetrators_by_year,
    get_1993_gap_info,
    get_reporting_bias_context,
)


def test_compute_missingness_by_column(sample_raw_df):
    """Verify missingness summary table outputs valid percentages."""
    res = compute_missingness_by_column(sample_raw_df)
    assert isinstance(res, pd.DataFrame)
    assert set(["column", "missing_count", "missing_pct", "valid_count"]).issubset(res.columns)
    assert (res["missing_pct"] >= 0.0).all()
    assert (res["missing_pct"] <= 100.0).all()


def test_compute_missingness_by_decade(synthetic_multidecade_df):
    """Verify missingness across decades returns a populated grid."""
    matrix = compute_missingness_by_decade(synthetic_multidecade_df)
    assert isinstance(matrix, pd.DataFrame)
    # Check decades exist as columns
    for dec in ["1970s", "1980s", "1990s", "2000s", "2010s"]:
        assert dec in matrix.columns
    # Check values are between 0 and 100
    assert (matrix.values >= 0.0).all()
    assert (matrix.values <= 100.0).all()


def test_compute_unknown_perpetrators_by_year(synthetic_multidecade_df):
    """Verify unknown perpetrator annual shares."""
    res = compute_unknown_perpetrators_by_year(synthetic_multidecade_df)
    assert isinstance(res, pd.DataFrame)
    assert "unknown_pct" in res.columns
    assert (res["unknown_pct"] >= 0.0).all()
    assert (res["unknown_pct"] <= 100.0).all()
    # 1993 must NOT be present in valid GTD years
    assert MISSING_YEAR not in res["iyear"].values


def test_compute_casualty_reporting_rate_by_year(synthetic_multidecade_df):
    """Verify casualty reporting rates are within 0-100%."""
    res = compute_casualty_reporting_rate_by_year(synthetic_multidecade_df)
    assert isinstance(res, pd.DataFrame)
    assert "known_rate_pct" in res.columns
    assert (res["known_rate_pct"] >= 0.0).all()
    assert (res["known_rate_pct"] <= 100.0).all()


def test_compute_coordinate_precision_stats(synthetic_multidecade_df):
    """Verify coordinate precision audit dictionary."""
    stats = compute_coordinate_precision_stats(synthetic_multidecade_df)
    assert "total_records" in stats
    assert "missing_coords_pct" in stats
    assert "pinpoint_coords_pct" in stats
    assert 0.0 <= stats["missing_coords_pct"] <= 100.0
    assert 0.0 <= stats["pinpoint_coords_pct"] <= 100.0


def test_compute_annual_data_quality_scores_properties(synthetic_multidecade_df):
    """Verify composite data quality score is bounded in [0, 100]."""
    scores_df = compute_annual_data_quality_scores(synthetic_multidecade_df)
    assert isinstance(scores_df, pd.DataFrame)
    assert "data_quality_score" in scores_df.columns
    assert (scores_df["data_quality_score"] >= 0.0).all()
    assert (scores_df["data_quality_score"] <= 100.0).all()
    assert MISSING_YEAR not in scores_df["iyear"].values


def test_gap_and_bias_information():
    """Verify metadata strings are non-empty and well-structured."""
    gap_info = get_1993_gap_info()
    assert "1993" in gap_info["year"]
    assert len(gap_info["cause"]) > 20

    bias_info = get_reporting_bias_context()
    assert isinstance(bias_info, list)
    assert len(bias_info) >= 3

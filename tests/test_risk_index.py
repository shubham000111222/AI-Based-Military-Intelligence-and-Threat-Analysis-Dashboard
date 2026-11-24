"""
Unit tests for risk_index.py.
Verifies:
1. Monotonicity: Adding incidents or casualties never lowers risk score.
2. Weight normalization: Arbitrary user weights are strictly normalized to sum to 1.0.
3. Boundedness: Risk scores stay within [0.0, 100.0].
4. Tier assignments adhere to Low/Medium/High/Critical.
5. Kendall's tau sensitivity benchmark calculation.
"""

import pandas as pd
import pytest

from src.risk_index import (
    calculate_risk_index,
    evaluate_ranking_stability,
    normalize_weights,
)


def test_normalize_weights():
    """Verify arbitrary positive weights normalize to 1.0."""
    raw = {"log_incidents": 2.0, "log_casualties": 2.0, "trend_slope": 1.0, "mass_casualty_ratio": 1.0}
    norm = normalize_weights(raw)
    assert abs(sum(norm.values()) - 1.0) < 1e-4
    assert norm["log_incidents"] == pytest.approx(2.0 / 6.0, rel=1e-3)

    # Edge case: all zeroes defaults to equal weights
    all_zero = {"log_incidents": 0.0, "log_casualties": 0.0, "trend_slope": 0.0, "mass_casualty_ratio": 0.0}
    norm_zero = normalize_weights(all_zero)
    assert abs(sum(norm_zero.values()) - 1.0) < 1e-4
    assert norm_zero["log_incidents"] == 0.25


def test_risk_score_monotonicity_casualties(synthetic_multidecade_df):
    """Monotonicity Rule: Increasing casualties for a country never lowers its risk score."""
    eval_year = 2016
    df_base = synthetic_multidecade_df.copy()

    # Calculate baseline
    risk_base = calculate_risk_index(df_base, year=eval_year)
    if risk_base.empty:
        pytest.skip(f"No incidents in year {eval_year}")

    target_country = risk_base.iloc[0]["country_txt"]
    base_score = risk_base.loc[risk_base["country_txt"] == target_country, "risk_score"].iloc[0]

    # Artificially inject additional casualties for that country in that year
    df_higher_cas = df_base.copy()
    mask = (df_higher_cas["country_txt"] == target_country) & (df_higher_cas["iyear"] == eval_year)
    df_higher_cas.loc[mask, "nkill"] += 100.0
    df_higher_cas.loc[mask, "ncasualty"] += 100.0

    risk_higher = calculate_risk_index(df_higher_cas, year=eval_year)
    higher_score = risk_higher.loc[risk_higher["country_txt"] == target_country, "risk_score"].iloc[0]

    # Higher casualties must result in equal or greater risk score
    assert higher_score >= base_score


def test_risk_score_monotonicity_incidents(synthetic_multidecade_df):
    """Monotonicity Rule: Increasing incident count never lowers risk score."""
    eval_year = 2016
    df_base = synthetic_multidecade_df.copy()

    risk_base = calculate_risk_index(df_base, year=eval_year)
    if risk_base.empty:
        pytest.skip(f"No incidents in year {eval_year}")

    target_country = risk_base.iloc[0]["country_txt"]
    base_score = risk_base.loc[risk_base["country_txt"] == target_country, "risk_score"].iloc[0]

    # Inject additional incidents for that country in that year
    sample_row = df_base[df_base["country_txt"] == target_country].iloc[0].to_dict()
    sample_row["iyear"] = eval_year
    sample_row["nkill"] = 5.0
    sample_row["nwound"] = 5.0
    sample_row["ncasualty"] = 10.0

    extra_rows = pd.DataFrame([sample_row] * 5)
    df_higher_inc = pd.concat([df_base, extra_rows], ignore_index=True)

    risk_higher = calculate_risk_index(df_higher_inc, year=eval_year)
    higher_score = risk_higher.loc[risk_higher["country_txt"] == target_country, "risk_score"].iloc[0]

    assert higher_score >= base_score


def test_risk_score_boundedness_and_tiers(synthetic_multidecade_df):
    """Verify composite risk score is bounded in [0, 100] and tiers are valid."""
    eval_year = 2016
    risk_df = calculate_risk_index(synthetic_multidecade_df, year=eval_year)
    if risk_df.empty:
        pytest.skip(f"No incidents in year {eval_year}")

    assert (risk_df["risk_score"] >= 0.0).all()
    assert (risk_df["risk_score"] <= 100.0).all()

    valid_tiers = {"Low", "Medium", "High", "Critical"}
    assert set(risk_df["risk_tier"]).issubset(valid_tiers)


def test_evaluate_ranking_stability_kendall_tau():
    """Verify Kendall's tau sensitivity benchmark calculation."""
    df_a = pd.DataFrame({
        "country_txt": ["Country A", "Country B", "Country C"],
        "risk_score": [90.0, 70.0, 50.0],
        "rank": [1, 2, 3],
    })
    # Identical rankings -> tau = 1.0
    tau_identical, _ = evaluate_ranking_stability(df_a, df_a)
    assert tau_identical == 1.0

    # Inverted rankings -> tau = -1.0
    df_b = pd.DataFrame({
        "country_txt": ["Country A", "Country B", "Country C"],
        "risk_score": [50.0, 70.0, 90.0],
        "rank": [3, 2, 1],
    })
    tau_inverted, _ = evaluate_ranking_stability(df_a, df_b)
    assert tau_inverted == -1.0

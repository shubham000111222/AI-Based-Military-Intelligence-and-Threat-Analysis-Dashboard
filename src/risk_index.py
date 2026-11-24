"""
Composite Risk Index calculation and scenario simulation module.
Computes multi-criteria sovereign risk scores per country-year:
1. Log-transformed incident volume: log(1 + count)
2. Log-transformed casualty volume: log(1 + casualties) with optional outlier cap
3. 3-year momentum / trend slope over trailing 3 years
4. Mass-casualty vulnerability ratio: share of attacks with >= threshold casualties
Enforces strict monotonicity, weight normalization, quantile-based risk tiers,
and Kendall's tau ranking sensitivity analysis.
"""

import logging
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import kendalltau

from src.config import DEFAULT_RISK_WEIGHTS, MASS_CASUALTY_THRESHOLD

logger = logging.getLogger(__name__)

# Documented quantile thresholds for risk tiers
TIER_QUANTILES: Dict[str, Tuple[float, float]] = {
    "Low": (0.0, 0.40),       # 0th to 40th percentile
    "Medium": (0.40, 0.70),   # 40th to 70th percentile
    "High": (0.70, 0.90),     # 70th to 90th percentile
    "Critical": (0.90, 1.00), # Top 10th percentile
}


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Ensure component weights are non-negative and strictly sum to 1.0.

    Parameters
    ----------
    weights : dict
        Raw weights for components.

    Returns
    -------
    dict
        Normalized weights summing to 1.0.
    """
    cleaned = {k: max(0.0, float(v)) for k, v in weights.items()}
    total = sum(cleaned.values())
    if total <= 0:
        # Fall back to equal weights
        n = len(cleaned)
        return {k: 1.0 / n for k in cleaned}
    return {k: round(v / total, 6) for k, v in cleaned.items()}


def compute_trailing_3yr_slopes(
    df: pd.DataFrame,
    target_year: int,
) -> Dict[str, float]:
    """
    Compute 3-year incident trend momentum (slope) for each country
    over trailing years [target_year - 2, target_year - 1, target_year].

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame.
    target_year : int
        Observation evaluation year.

    Returns
    -------
    dict
        Mapping of country_txt -> linear trend slope.
    """
    eval_years = [target_year - 2, target_year - 1, target_year]
    sub = df[df["iyear"].isin(eval_years)]

    counts = (
        sub.groupby(["country_txt", "iyear"])
        .size()
        .unstack(fill_value=0)
    )

    slopes: Dict[str, float] = {}
    x = np.array([0, 1, 2], dtype=float)

    for country in counts.index:
        y_vals = [counts.loc[country].get(yr, 0) for yr in eval_years]
        # Linear regression slope: cov(x, y) / var(x)
        # For x = [0, 1, 2], var(x) = 2/3, mean(x) = 1
        slope = float(np.polyfit(x, y_vals, 1)[0]) if len(eval_years) == 3 else 0.0
        slopes[country] = slope

    return slopes


def compute_country_risk_components(
    df: pd.DataFrame,
    year: int,
    casualty_cap: Optional[float] = None,
    mass_casualty_threshold: int = MASS_CASUALTY_THRESHOLD,
) -> pd.DataFrame:
    """
    Extract raw risk indicators for each country in the evaluation year.

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame.
    year : int
        Evaluation year.
    casualty_cap : float, optional
        Maximum casualty cap per incident to test sensitivity to extreme single-event outliers.
    mass_casualty_threshold : int
        Casualty cutoff defining mass-casualty events (default: 10).

    Returns
    -------
    pd.DataFrame
        Table with raw component values per country.
    """
    df_yr = df[df["iyear"] == year].copy()
    if df_yr.empty:
        return pd.DataFrame()

    if casualty_cap is not None and casualty_cap > 0:
        df_yr["eval_casualty"] = df_yr["ncasualty"].clip(upper=casualty_cap)
    else:
        df_yr["eval_casualty"] = df_yr["ncasualty"]

    df_yr["is_mass_casualty"] = (df_yr["eval_casualty"] >= mass_casualty_threshold).astype(int)

    # Base aggregations per country
    agg = (
        df_yr.groupby("country_txt")
        .agg(
            incidents=("iyear", "count"),
            casualties=("eval_casualty", "sum"),
            mass_casualties=("is_mass_casualty", "sum"),
            region_txt=("region_txt", "first"),
        )
        .reset_index()
    )

    # Component 1: Log incident count
    agg["log_incidents"] = np.log1p(agg["incidents"])

    # Component 2: Log casualties
    agg["log_casualties"] = np.log1p(agg["casualties"])

    # Component 3: 3-year momentum slope
    trend_slopes = compute_trailing_3yr_slopes(df, target_year=year)
    agg["trend_slope"] = agg["country_txt"].map(trend_slopes).fillna(0.0)

    # Component 4: Mass casualty ratio
    agg["mass_casualty_ratio"] = (agg["mass_casualties"] / agg["incidents"]).fillna(0.0)

    return agg


def min_max_scale(series: pd.Series) -> pd.Series:
    """Safely min-max scale a series to [0.0, 1.0]."""
    s_min = series.min()
    s_max = series.max()
    if s_max > s_min:
        return (series - s_min) / (s_max - s_min)
    return pd.Series(0.0, index=series.index)


def assign_risk_tier(scores: pd.Series) -> pd.Series:
    """
    Assign qualitative risk tiers based on documented quantile thresholds:
    - Low: 0th to 40th percentile
    - Medium: 40th to 70th percentile
    - High: 70th to 90th percentile
    - Critical: Top 10th percentile
    """
    q_low = scores.quantile(TIER_QUANTILES["Low"][1])
    q_med = scores.quantile(TIER_QUANTILES["Medium"][1])
    q_high = scores.quantile(TIER_QUANTILES["High"][1])

    def _tier(val: float) -> str:
        if val <= q_low:
            return "Low"
        elif val <= q_med:
            return "Medium"
        elif val <= q_high:
            return "High"
        else:
            return "Critical"

    return scores.apply(_tier)


def calculate_risk_index(
    df: pd.DataFrame,
    year: int,
    weights: Optional[Dict[str, float]] = None,
    casualty_cap: Optional[float] = None,
) -> pd.DataFrame:
    """
    Compute Composite Strategic Country Risk Index (0 to 100) for a given year.

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame.
    year : int
        Target year for risk scoring.
    weights : dict, optional
        Custom component weights. If None, uses DEFAULT_RISK_WEIGHTS.
    casualty_cap : float, optional
        Optional cap on casualties per incident.

    Returns
    -------
    pd.DataFrame
        Ranked country risk table with composite score, component scores, and risk tier.
    """
    norm_w = normalize_weights(weights if weights is not None else DEFAULT_RISK_WEIGHTS)

    raw_comp = compute_country_risk_components(df, year=year, casualty_cap=casualty_cap)
    if raw_comp.empty:
        return pd.DataFrame()

    # Min-max normalize each of the 4 components to [0, 1]
    norm_inc = min_max_scale(raw_comp["log_incidents"])
    norm_cas = min_max_scale(raw_comp["log_casualties"])
    norm_trend = min_max_scale(raw_comp["trend_slope"])
    norm_mass = min_max_scale(raw_comp["mass_casualty_ratio"])

    # Composite weighted score (0 to 100)
    raw_comp["norm_incidents"] = (norm_inc * 100).round(2)
    raw_comp["norm_casualties"] = (norm_cas * 100).round(2)
    raw_comp["norm_trend"] = (norm_trend * 100).round(2)
    raw_comp["norm_mass_casualty"] = (norm_mass * 100).round(2)

    composite = (
        norm_w.get("log_incidents", 0.3) * raw_comp["norm_incidents"]
        + norm_w.get("log_casualties", 0.3) * raw_comp["norm_casualties"]
        + norm_w.get("trend_slope", 0.2) * raw_comp["norm_trend"]
        + norm_w.get("mass_casualty_ratio", 0.2) * raw_comp["norm_mass_casualty"]
    )

    raw_comp["risk_score"] = composite.round(2)
    raw_comp["risk_tier"] = assign_risk_tier(raw_comp["risk_score"])

    # Rank countries (Rank 1 = Highest Risk)
    raw_comp = raw_comp.sort_values("risk_score", ascending=False).reset_index(drop=True)
    raw_comp["rank"] = raw_comp.index + 1

    return raw_comp


def evaluate_ranking_stability(
    baseline_df: pd.DataFrame,
    simulated_df: pd.DataFrame,
) -> Tuple[float, pd.DataFrame]:
    """
    Benchmark rank stability between baseline default weights and simulated custom weights
    using Kendall's tau correlation. Calculates per-country rank change.

    Parameters
    ----------
    baseline_df : pd.DataFrame
        Ranked DataFrame with default weights.
    simulated_df : pd.DataFrame
        Ranked DataFrame with scenario weights.

    Returns
    -------
    Tuple[float, pd.DataFrame]
        1. tau: Kendall's tau rank correlation (-1.0 to 1.0).
        2. comparison_df: DataFrame showing baseline rank, simulated rank, and rank change.
    """
    merged = pd.merge(
        baseline_df[["country_txt", "risk_score", "rank"]].rename(
            columns={"risk_score": "base_score", "rank": "base_rank"}
        ),
        simulated_df[["country_txt", "risk_score", "rank"]].rename(
            columns={"risk_score": "sim_score", "rank": "sim_rank"}
        ),
        on="country_txt",
        how="inner",
    )

    if len(merged) < 2:
        return 1.0, merged

    tau, _ = kendalltau(merged["base_rank"], merged["sim_rank"])
    merged["rank_change"] = merged["base_rank"] - merged["sim_rank"]  # Positive means moved UP in risk rank
    merged["tau"] = round(float(tau), 4)

    return round(float(tau), 4), merged.sort_values("sim_rank")

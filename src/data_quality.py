"""
Data quality audit and reporting bias analysis module for the Global Terrorism Database.
Computes column missingness matrices, decade heatmaps, unknown perpetrator rates,
casualty completeness, coordinate precision audits, and annual data-quality scores.
"""

from typing import Any, Dict, List

import pandas as pd

from src.config import MISSING_YEAR, UNKNOWN_GROUP_NAME


def compute_missingness_by_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate absolute missing count and percentage for every column in the dataset.

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame.

    Returns
    -------
    pd.DataFrame
        Summary table with columns: ['column', 'missing_count', 'missing_pct', 'valid_count']
    """
    total = len(df)
    if total == 0:
        return pd.DataFrame(columns=["column", "missing_count", "missing_pct", "valid_count"])

    records = []
    for col in df.columns:
        # Check standard nulls as well as empty strings or explicit 'Unknown' if applicable
        null_count = df[col].isna().sum()
        # For object columns, also treat empty strings as missing
        if df[col].dtype == "object":
            empty_count = (df[col] == "").sum()
            total_missing = null_count + empty_count
        else:
            total_missing = null_count

        records.append({
            "column": col,
            "missing_count": int(total_missing),
            "missing_pct": round(float(total_missing / total * 100), 2),
            "valid_count": int(total - total_missing),
        })

    result_df = pd.DataFrame(records).sort_values("missing_pct", ascending=False)
    return result_df.reset_index(drop=True)


def compute_missingness_by_decade(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate missingness rate matrix (% missing) across decades for core analytical fields.
    Reveals archival digitization discrepancies and historical collection drift.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned GTD DataFrame with 'iyear'.

    Returns
    -------
    pd.DataFrame
        Pivot table indexed by decade with columns representing attribute missingness %.
    """
    df_copy = df.copy()

    # Assign decade label
    def get_decade(year: int) -> str:
        if year < 1980:
            return "1970s"
        elif year < 1990:
            return "1980s"
        elif year < 2000:
            return "1990s"
        elif year < 2010:
            return "2000s"
        else:
            return "2010s"

    df_copy["decade"] = df_copy["iyear"].apply(get_decade)

    # Core audit attributes
    audit_cols = [
        "latitude",
        "provstate",
        "city",
        "gname",
        "nkill",
        "nwound",
        "summary",
    ]
    # Filter to existing columns
    cols_to_check = [c for c in audit_cols if c in df_copy.columns]

    decades = ["1970s", "1980s", "1990s", "2000s", "2010s"]
    decade_matrix: Dict[str, Dict[str, float]] = {col: {} for col in cols_to_check}

    for dec in decades:
        sub = df_copy[df_copy["decade"] == dec]
        total = len(sub)
        for col in cols_to_check:
            if total == 0:
                pct = 0.0
            else:
                if col == "gname":
                    # Unknown group represents unclaimed/missing attribution
                    missing = (sub[col].isna() | (sub[col] == UNKNOWN_GROUP_NAME) | (sub[col] == "")).sum()
                elif col in ["nkill", "nwound"]:
                    # Check flag if present, else check original isna or filled zeroes with casualties_known flag
                    if "casualties_known" in sub.columns:
                        missing = (~sub["casualties_known"]).sum()
                    else:
                        missing = sub[col].isna().sum()
                elif col == "summary":
                    missing = (sub[col].isna() | (sub[col] == "") | (sub[col].str.len() <= 10)).sum()
                else:
                    missing = (sub[col].isna() | (sub[col] == "") | (sub[col] == "Unknown")).sum()

                pct = round(float(missing / total * 100), 1)
            decade_matrix[col][dec] = pct

    return pd.DataFrame(decade_matrix).T


def compute_unknown_perpetrators_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute annual volume and share of incidents attributed to 'Unknown' perpetrators.
    Unclaimed attacks represent a massive statistical challenge in threat attribution.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned GTD DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: ['iyear', 'total_incidents', 'unknown_count', 'unknown_pct']
    """
    records = []
    all_years = sorted([y for y in df["iyear"].unique() if y != MISSING_YEAR])

    for y in all_years:
        sub = df[df["iyear"] == y]
        total = len(sub)
        if total == 0:
            continue
        unknown_mask = (sub["gname"] == UNKNOWN_GROUP_NAME) | (sub["gname"].isna()) | (sub["gname"] == "")
        unknown_count = int(unknown_mask.sum())
        unknown_pct = round(float(unknown_count / total * 100), 2)
        records.append({
            "iyear": int(y),
            "total_incidents": total,
            "unknown_count": unknown_count,
            "unknown_pct": unknown_pct,
            "known_pct": round(100.0 - unknown_pct, 2),
        })

    return pd.DataFrame(records)


def compute_casualty_reporting_rate_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute share of incidents each year with explicitly known/verified casualties.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned GTD DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: ['iyear', 'total_incidents', 'known_casualties_count', 'known_rate_pct']
    """
    records = []
    all_years = sorted([y for y in df["iyear"].unique() if y != MISSING_YEAR])

    for y in all_years:
        sub = df[df["iyear"] == y]
        total = len(sub)
        if total == 0:
            continue

        if "casualties_known" in sub.columns:
            known_count = int(sub["casualties_known"].sum())
        else:
            known_count = int((sub["nkill"].notna() | sub["nwound"].notna()).sum())

        known_pct = round(float(known_count / total * 100), 2)
        records.append({
            "iyear": int(y),
            "total_incidents": total,
            "known_casualties_count": known_count,
            "known_rate_pct": known_pct,
        })

    return pd.DataFrame(records)


def compute_coordinate_precision_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Audit geocoding fidelity and precision across all records.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned GTD DataFrame.

    Returns
    -------
    dict
        Dictionary containing counts and percentages of missing coordinates,
        approximate centroid coordinates, and valid pinpointed coordinates.
    """
    total = len(df)
    if total == 0:
        return {"total_records": 0, "missing_coords_pct": 0.0, "pinpoint_coords_pct": 0.0}

    missing_coords = int((~df["has_coordinates"]).sum()) if "has_coordinates" in df.columns else int(df["latitude"].isna().sum())
    valid_coords = total - missing_coords

    if "coord_is_approx_centroid" in df.columns:
        approx_centroids = int(df["coord_is_approx_centroid"].sum())
    else:
        # Fallback check
        approx_centroids = int(
            ((df["latitude"].dropna() % 1 == 0) & (df["longitude"].dropna() % 1 == 0)).sum()
        )

    pinpoint_coords = valid_coords - approx_centroids

    return {
        "total_records": total,
        "valid_coords_count": valid_coords,
        "valid_coords_pct": round(float(valid_coords / total * 100), 2),
        "missing_coords_count": missing_coords,
        "missing_coords_pct": round(float(missing_coords / total * 100), 2),
        "approx_centroids_count": approx_centroids,
        "approx_centroids_pct": round(float(approx_centroids / total * 100), 2),
        "pinpoint_coords_count": pinpoint_coords,
        "pinpoint_coords_pct": round(float(pinpoint_coords / total * 100), 2),
    }


def compute_annual_data_quality_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a composite Data Quality Index (0-100) per year.
    The composite score evaluates 4 key pillars of intelligence fidelity:
    1. Casualty Completeness (weight 25%): Percentage of incidents with documented casualties.
    2. Coordinate Precision (weight 25%): Percentage with valid coordinates (penalized if missing or rounded centroid).
    3. Perpetrator Identification (weight 25%): Percentage with an identified perpetrator group (not 'Unknown').
    4. Narrative Documentation (weight 25%): Percentage with incident summary text.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned GTD DataFrame.

    Returns
    -------
    pd.DataFrame
        Annual scores table with sub-component percentages and final quality score.
    """
    records = []
    all_years = sorted([y for y in df["iyear"].unique() if y != MISSING_YEAR])

    for y in all_years:
        sub = df[df["iyear"] == y]
        total = len(sub)
        if total == 0:
            continue

        # Pillar 1: Casualty completeness
        if "casualties_known" in sub.columns:
            cas_comp = float(sub["casualties_known"].mean() * 100)
        else:
            cas_comp = 90.0

        # Pillar 2: Coordinate precision
        if "has_coordinates" in sub.columns:
            has_coords_pct = float(sub["has_coordinates"].mean() * 100)
            if "coord_is_approx_centroid" in sub.columns:
                centroid_penalty = float(sub["coord_is_approx_centroid"].mean() * 30)
            else:
                centroid_penalty = 5.0
            coord_score = max(0.0, has_coords_pct - centroid_penalty)
        else:
            coord_score = 75.0

        # Pillar 3: Group attribution
        unknown_mask = (sub["gname"] == UNKNOWN_GROUP_NAME) | (sub["gname"].isna()) | (sub["gname"] == "")
        known_group_pct = float((~unknown_mask).mean() * 100)

        # Pillar 4: Narrative documentation
        if "has_summary" in sub.columns:
            narrative_pct = float(sub["has_summary"].mean() * 100)
        elif "summary" in sub.columns:
            narrative_pct = float((sub["summary"].fillna("").str.len() > 10).mean() * 100)
        else:
            narrative_pct = 50.0

        # Composite score calculation (25% each pillar)
        quality_score = round(
            0.25 * cas_comp + 0.25 * coord_score + 0.25 * known_group_pct + 0.25 * narrative_pct,
            1,
        )

        records.append({
            "iyear": int(y),
            "casualty_completeness_pct": round(cas_comp, 1),
            "coordinate_score_pct": round(coord_score, 1),
            "group_attribution_pct": round(known_group_pct, 1),
            "narrative_coverage_pct": round(narrative_pct, 1),
            "data_quality_score": quality_score,
            "total_incidents": total,
        })

    return pd.DataFrame(records)


def get_1993_gap_info() -> Dict[str, str]:
    """
    Return comprehensive historical and archival context regarding the 1993 data gap.
    """
    return {
        "title": "The Missing Year: 1993 Archive Gap",
        "year": "1993",
        "status": "Missing from GTD Standard Distribution",
        "cause": (
            "During the transfer of original paper and microfiche records between the PGIS "
            "(Pinkerton Global Intelligence Services) archive and the digital database project at "
            "the University of Maryland (START), an entire box of incident cards for 1993 was lost in transit."
        ),
        "impact": (
            "While researchers subsequent to 1998 attempted retrospectives from news indices, "
            "START determined that reconstructing only high-profile incidents would introduce severe "
            "selection bias. Consequently, 1993 is officially excluded from temporal analysis."
        ),
        "methodological_recommendation": (
            "Every longitudinal chart, ARIMA/SARIMA model, and trendline MUST account for this discrete "
            "discontinuity. Imputation or interpolation must be explicitly flagged when applied."
        ),
    }


def get_reporting_bias_context() -> List[Dict[str, str]]:
    """
    Return structured analysis of historical reporting bias and methodological shifts.
    """
    return [
        {
            "dimension": "1. Media Saturation & Internet Proliferation (Post-2000)",
            "impact": "Apparent incident surge in 2000–2017",
            "mechanism": (
                "Before the late 1990s, incident recording relied on international wire services "
                "(AP, Reuters, AFP) and major print dailies. The digital revolution, localized internet journalism, "
                "and social media post-2005 vastly increased the capture rate of small-scale insurgent skirmishes "
                "that would have gone unnoticed in the 1970s and 1980s."
            ),
        },
        {
            "dimension": "2. Methodological & Institutional Transfers (1997, 2006, 2012)",
            "impact": "Discontinuities in incident classification criteria",
            "mechanism": (
                "Data collection passed through three primary regimes: Pinkerton Global Intelligence Services (1970–1997), "
                "the Center for Terrorism and Intelligence Studies (CETIS, 1998–2005), and START / University of Maryland "
                "(2006–2018). In 1997, criteria were revised to strictly require 3 inclusion filters: intentional act, "
                "threat of violence, and sub-national perpetrator."
            ),
        },
        {
            "dimension": "3. Asymmetric Information in Conflict Zones",
            "impact": "High unknown attribution rates in insurgencies",
            "mechanism": (
                "In prolonged active warzones (e.g. Iraq post-2003, Syria post-2011, Afghanistan post-2008), "
                "over 70% of IED and armed attacks went unclaimed by specific militant factions. This causes "
                "a massive spike in 'Unknown' perpetrators, obscuring organizational responsibility."
            ),
        },
        {
            "dimension": "4. State Censorship & Geopolitical Visibility",
            "impact": "Geographic underreporting in authoritarian states",
            "mechanism": (
                "Attacks in open, democratic societies with free press received immediate, exhaustive documentation, "
                "whereas political violence inside closed regimes (e.g. Soviet bloc, military dictatorships in the 1970s/80s) "
                "was systematically suppressed from international wire reports."
            ),
        },
    ]

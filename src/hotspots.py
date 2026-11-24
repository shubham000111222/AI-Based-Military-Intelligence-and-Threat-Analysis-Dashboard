"""
Geospatial hotspot detection using DBSCAN with haversine distance metric.
Clusters geographic incident coordinates into tactical activity zones,
calculates spatial centroids, casualty aggregates, and dominant tactical signatures.
"""

import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

from src.config import UNKNOWN_GROUP_NAME

logger = logging.getLogger(__name__)

# Mean Earth radius in kilometers for spherical haversine projections
EARTH_RADIUS_KM: float = 6371.0088


def filter_valid_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter DataFrame strictly to incidents with valid latitude and longitude.
    Preserves original indices and ensures coordinate bounds.

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame.

    Returns
    -------
    pd.DataFrame
        Subset with valid, non-null spherical coordinates.
    """
    if "has_coordinates" in df.columns:
        valid_mask = df["has_coordinates"] & df["latitude"].notna() & df["longitude"].notna()
    else:
        valid_mask = df["latitude"].notna() & df["longitude"].notna()

    # Enforce standard spherical bounds
    valid_mask = (
        valid_mask
        & (df["latitude"] >= -90.0)
        & (df["latitude"] <= 90.0)
        & (df["longitude"] >= -180.0)
        & (df["longitude"] <= 180.0)
    )
    return df[valid_mask].copy()


def compute_spatial_clusters(
    df: pd.DataFrame,
    eps_km: float = 75.0,
    min_samples: int = 10,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Execute DBSCAN density clustering over geographic incident coordinates using haversine metric.

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame (will be filtered to valid coordinates).
    eps_km : float
        Maximum spherical neighborhood distance in kilometers (default: 75.0 km).
    min_samples : int
        Minimum incident count required to form a dense spatial cluster core (default: 10).

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        1. df_clustered: DataFrame of valid-coord incidents with 'cluster_id' column (-1 = noise).
        2. cluster_summary: Summary DataFrame of identified clusters ordered by incident volume.
    """
    df_valid = filter_valid_coordinates(df)

    if len(df_valid) == 0:
        empty_clustered = df_valid.assign(cluster_id=pd.Series(dtype=int))
        empty_summary = pd.DataFrame(columns=[
            "cluster_id", "incident_count", "total_fatalities", "total_wounded",
            "total_casualties", "centroid_lat", "centroid_lon", "primary_country",
            "primary_region", "primary_attack_type", "primary_group", "year_range",
        ])
        return empty_clustered, empty_summary

    # Convert degrees to radians for haversine metric: shape (N, 2) [latitude_rad, longitude_rad]
    coords_rad = np.radians(df_valid[["latitude", "longitude"]].values)

    # Convert epsilon in kilometers to radians
    eps_rad = eps_km / EARTH_RADIUS_KM

    # Run DBSCAN
    db = DBSCAN(
        eps=eps_rad,
        min_samples=min_samples,
        metric="haversine",
        algorithm="ball_tree",
    )
    db.fit(coords_rad)

    df_valid["cluster_id"] = db.labels_

    # Generate Cluster Summary
    clusters = sorted([c for c in np.unique(db.labels_) if c != -1])
    summary_records: List[Dict] = []

    for cid in clusters:
        sub = df_valid[df_valid["cluster_id"] == cid]
        count = len(sub)
        tot_kill = float(sub["nkill"].sum())
        tot_wound = float(sub["nwound"].sum())
        tot_cas = float(sub["ncasualty"].sum()) if "ncasualty" in sub.columns else tot_kill + tot_wound

        # Geographic centroid (mean coordinate)
        c_lat = round(float(sub["latitude"].mean()), 4)
        c_lon = round(float(sub["longitude"].mean()), 4)

        # Dominant tactical attributes
        top_country = sub["country_txt"].mode()[0] if not sub["country_txt"].empty else "Unknown"
        top_region = sub["region_txt"].mode()[0] if not sub["region_txt"].empty else "Unknown"
        top_attack = sub["attacktype1_txt"].mode()[0] if not sub["attacktype1_txt"].empty else "Unknown"

        # Dominant identified group (excluding 'Unknown' if possible)
        known_groups = sub[sub["gname"] != UNKNOWN_GROUP_NAME]["gname"]
        if not known_groups.empty:
            top_group = known_groups.mode()[0]
        else:
            top_group = UNKNOWN_GROUP_NAME

        min_yr = int(sub["iyear"].min())
        max_yr = int(sub["iyear"].max())
        yr_range = f"{min_yr}–{max_yr}" if min_yr != max_yr else str(min_yr)

        summary_records.append({
            "cluster_id": int(cid),
            "incident_count": count,
            "total_fatalities": int(tot_kill),
            "total_wounded": int(tot_wound),
            "total_casualties": int(tot_cas),
            "centroid_lat": c_lat,
            "centroid_lon": c_lon,
            "primary_country": top_country,
            "primary_region": top_region,
            "primary_attack_type": top_attack,
            "primary_group": top_group,
            "year_range": yr_range,
        })

    summary_df = pd.DataFrame(summary_records)
    if not summary_df.empty:
        summary_df = summary_df.sort_values("incident_count", ascending=False).reset_index(drop=True)

    return df_valid, summary_df

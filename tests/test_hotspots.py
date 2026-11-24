"""
Unit tests for hotspots.py geospatial clustering with DBSCAN and haversine metric.
"""

import numpy as np
import pandas as pd
import pytest

from src.hotspots import (
    EARTH_RADIUS_KM,
    compute_spatial_clusters,
    filter_valid_coordinates,
)


@pytest.fixture
def spatial_clusters_df():
    """
    Generate synthetic data with two clearly separated geographic clusters:
    1. Cluster near London (51.5074 N, -0.1278 W) - 15 points
    2. Cluster near Baghdad (33.3152 N, 44.3661 E) - 15 points
    3. Isolated outliers (noise points) - 3 points
    4. Missing coordinates - 3 points
    """
    np.random.seed(42)

    # London cluster (~5km dispersion)
    lat_london = 51.5074 + np.random.normal(0, 0.04, 15)
    lon_london = -0.1278 + np.random.normal(0, 0.04, 15)

    # Baghdad cluster (~5km dispersion)
    lat_baghdad = 33.3152 + np.random.normal(0, 0.04, 15)
    lon_baghdad = 44.3661 + np.random.normal(0, 0.04, 15)

    # Outliers
    lat_outliers = [0.0, -45.0, 70.0]
    lon_outliers = [0.0, 120.0, -140.0]

    # Missing
    lat_missing = [np.nan, 25.0, np.nan]
    lon_missing = [np.nan, np.nan, 30.0]

    all_lats = np.concatenate([lat_london, lat_baghdad, lat_outliers, lat_missing])
    all_lons = np.concatenate([lon_london, lon_baghdad, lon_outliers, lon_missing])
    n = len(all_lats)

    df = pd.DataFrame({
        "iyear": np.random.choice([2005, 2006, 2007], size=n),
        "latitude": all_lats,
        "longitude": all_lons,
        "country_txt": ["United Kingdom"] * 15 + ["Iraq"] * 15 + ["Outlier"] * 3 + ["Missing"] * 3,
        "region_txt": ["Western Europe"] * 15 + ["Middle East"] * 15 + ["Other"] * 6,
        "attacktype1_txt": ["Bombing/Explosion"] * n,
        "gname": ["Group A"] * 15 + ["Group B"] * 15 + ["Unknown"] * 6,
        "nkill": [1.0] * n,
        "nwound": [2.0] * n,
        "ncasualty": [3.0] * n,
        "has_coordinates": ~np.isnan(all_lats) & ~np.isnan(all_lons),
    })
    return df


def test_filter_valid_coordinates(spatial_clusters_df):
    """Verify that rows with missing or invalid coordinates are dropped."""
    df_valid = filter_valid_coordinates(spatial_clusters_df)

    # 33 valid points expected (15 London + 15 Baghdad + 3 outliers)
    assert len(df_valid) == 33
    assert df_valid["latitude"].isna().sum() == 0
    assert df_valid["longitude"].isna().sum() == 0


def test_compute_spatial_clusters_identifies_clusters(spatial_clusters_df):
    """Verify DBSCAN identifies the two dense clusters with eps=50km and min_samples=10."""
    df_clustered, summary_df = compute_spatial_clusters(
        spatial_clusters_df,
        eps_km=50.0,
        min_samples=10,
    )

    # Exactly 2 dense clusters should be discovered
    assert len(summary_df) == 2

    # Cluster IDs must be 0 and 1
    assert set(summary_df["cluster_id"]) == {0, 1}

    # Verify both clusters have at least 10 incidents
    assert (summary_df["incident_count"] >= 10).all()

    # Verify centroids match expected regions
    countries = summary_df["primary_country"].tolist()
    assert "United Kingdom" in countries
    assert "Iraq" in countries


def test_compute_spatial_clusters_empty_handling():
    """Verify robust handling of empty DataFrames."""
    empty_df = pd.DataFrame(columns=["latitude", "longitude", "has_coordinates", "nkill", "nwound"])
    df_clustered, summary_df = compute_spatial_clusters(empty_df)

    assert len(df_clustered) == 0
    assert len(summary_df) == 0
    assert "centroid_lat" in summary_df.columns


def test_earth_radius_constant():
    """Verify spherical Earth radius constant sanity."""
    assert 6370.0 < EARTH_RADIUS_KM < 6372.0

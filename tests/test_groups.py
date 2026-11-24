"""
Unit tests for groups.py behavioral profiling and clustering.
"""

import numpy as np
import pandas as pd

from src.groups import (
    cluster_and_project_groups,
    extract_group_behavior_vectors,
    get_group_dossier,
)


def test_extract_group_behavior_vectors(synthetic_multidecade_df):
    """Verify behavioral vector construction and metadata dimensions."""
    meta_df, behavior_df, feat_cols = extract_group_behavior_vectors(
        synthetic_multidecade_df,
        min_incidents=10,
    )

    assert len(meta_df) > 0
    assert len(behavior_df) == len(meta_df)
    assert not behavior_df.isna().any().any()

    # Required metadata fields
    expected_meta = ["incidents", "fatalities", "mean_casualties", "start_year", "end_year"]
    for col in expected_meta:
        assert col in meta_df.columns


def test_cluster_and_project_groups(synthetic_multidecade_df):
    """Verify KMeans clustering and 2D PCA projection."""
    groups_df, cluster_names = cluster_and_project_groups(
        synthetic_multidecade_df,
        min_incidents=10,
        n_clusters=3,
    )

    assert "gname" in groups_df.columns
    assert "cluster_id" in groups_df.columns
    assert "cluster_label" in groups_df.columns
    assert "pca_x" in groups_df.columns
    assert "pca_y" in groups_df.columns

    # Verify 2D coordinates are valid finite numbers
    assert np.isfinite(groups_df["pca_x"]).all()
    assert np.isfinite(groups_df["pca_y"]).all()

    # Cluster labels should be assigned
    assert len(cluster_names) <= 3


def test_get_group_dossier(synthetic_multidecade_df):
    """Verify group dossier extraction."""
    # Find a valid group
    valid_group = synthetic_multidecade_df[synthetic_multidecade_df["gname"] != "Unknown"]["gname"].iloc[0]

    dossier = get_group_dossier(synthetic_multidecade_df, valid_group)

    assert dossier["gname"] == valid_group
    assert dossier["total_incidents"] > 0
    assert "top_countries" in dossier
    assert "top_tactics" in dossier
    assert "timeline" in dossier
    assert isinstance(dossier["timeline"], pd.DataFrame)

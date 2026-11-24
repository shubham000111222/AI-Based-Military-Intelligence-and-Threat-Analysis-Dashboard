"""
Unit tests for features.py.
Verifies:
1. Zero-leakage assertions trigger when banned post-attack variables are introduced.
2. Temporal split strictly enforces train <= 2012 and test 2013-2017 without temporal overlap.
3. Preprocessor safely handles unseen categories at inference time.
4. Target preparation merges rare categories to 'Other'.
"""

import numpy as np
import pandas as pd
import pytest

from src.config import BANNED_LEAKAGE_COLUMNS
from src.features import (
    ALLOWED_PRE_ATTACK_FEATURES,
    TOP_ATTACK_TYPES,
    assert_no_leakage,
    create_preprocessor,
    get_temporal_split,
    prepare_target,
)


def test_assert_no_leakage_raises_on_banned_columns():
    """Verify that assert_no_leakage raises ValueError on banned columns."""
    for banned_col in BANNED_LEAKAGE_COLUMNS:
        cols = ["iyear", "country_txt", banned_col]
        with pytest.raises(ValueError, match="DATA LEAKAGE DETECTED"):
            assert_no_leakage(cols)


def test_assert_no_leakage_passes_on_valid_features():
    """Verify assert_no_leakage succeeds when only pre-attack features are present."""
    assert_no_leakage(ALLOWED_PRE_ATTACK_FEATURES)


def test_temporal_split_integrity(synthetic_multidecade_df):
    """Verify temporal train/test split has zero temporal overlap."""
    X_train, y_train, X_test, y_test = get_temporal_split(synthetic_multidecade_df)

    assert len(X_train) > 0
    assert len(X_test) > 0

    # Strict year boundary checks
    assert (X_train["iyear"] <= 2012).all()
    assert (X_test["iyear"] >= 2013).all()
    assert (X_test["iyear"] <= 2017).all()

    # Verify banned columns absent from X
    for banned in BANNED_LEAKAGE_COLUMNS:
        assert banned not in X_train.columns
        assert banned not in X_test.columns


def test_preprocessor_handles_unseen_categories():
    """Verify ColumnTransformer handles unseen categorical classes without exception."""
    df_train = pd.DataFrame({
        "iyear": [2010, 2011],
        "region_txt": ["Western Europe", "South Asia"],
        "country_txt": ["United Kingdom", "India"],
        "provstate": ["London", "Delhi"],
        "targtype1_txt": ["Military", "Police"],
        "weaptype1_txt": ["Explosives", "Firearms"],
        "gname": ["Group A", "Group B"],
        "latitude": [51.5, 28.6],
        "longitude": [-0.1, 77.2],
        "coord_missing": [0, 0],
    })

    # Test set contains brand new unseen categories
    df_test = pd.DataFrame({
        "iyear": [2015],
        "region_txt": ["Completely New Region"],
        "country_txt": ["Unseen Sovereign State"],
        "provstate": ["Alien District"],
        "targtype1_txt": ["Novel Target Type"],
        "weaptype1_txt": ["Exotic Weapon"],
        "gname": ["Newly Formed Group XYZ"],
        "latitude": [np.nan],
        "longitude": [np.nan],
        "coord_missing": [1],
    })

    preprocessor = create_preprocessor()
    X_train_proc = preprocessor.fit_transform(df_train)
    X_test_proc = preprocessor.transform(df_test)

    # Dimensionality must match
    assert X_train_proc.shape[1] == X_test_proc.shape[1]
    assert not np.isnan(X_test_proc).any()


def test_prepare_target_merges_rare():
    """Verify that rare or novel attack types are mapped to 'Other'."""
    raw_targets = pd.DataFrame({
        "attacktype1_txt": [
            "Bombing/Explosion",
            "Assassination",
            "Very Rare Exotic Cyber Incident",
            None,
        ]
    })
    target_clean = prepare_target(raw_targets)

    assert target_clean.iloc[0] == "Bombing/Explosion"
    assert target_clean.iloc[1] == "Assassination"
    assert target_clean.iloc[2] == "Other"
    assert target_clean.iloc[3] == "Other"
    assert set(target_clean).issubset(set(TOP_ATTACK_TYPES))

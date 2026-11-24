"""
Feature engineering and preprocessing pipeline for pre-attack classification.
Enforces strict zero-leakage constraints:
- Uses ONLY information available before the attack occurs:
  iyear, region_txt, country_txt, provstate, targtype1_txt, weaptype1_txt, gname, latitude, longitude.
- Explicitly bans and checks against post-attack variables:
  nkill, nwound, ncasualty, success, suicide, summary, casualties_known.
- Implements strict temporal train/test splitting (Train <= 2012, Test 2013-2017).
"""

import logging
from typing import List, Set, Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    BANNED_LEAKAGE_COLUMNS,
    TEST_MAX_YEAR,
    TEST_MIN_YEAR,
    TRAIN_MAX_YEAR,
)

logger = logging.getLogger(__name__)

# Primary allowed predictive features available prior to an attack
ALLOWED_PRE_ATTACK_FEATURES: List[str] = [
    "iyear",
    "region_txt",
    "country_txt",
    "provstate",
    "targtype1_txt",
    "weaptype1_txt",
    "gname",
    "latitude",
    "longitude",
]

# Standard target variable
TARGET_COLUMN: str = "attacktype1_txt"

# Core attack categories to retain (rare categories collapsed to 'Other')
TOP_ATTACK_TYPES: List[str] = [
    "Bombing/Explosion",
    "Armed Assault",
    "Assassination",
    "Hostage Taking (Kidnapping)",
    "Facility/Infrastructure Attack",
    "Other",
]


def assert_no_leakage(columns: List[str]) -> None:
    """
    Assert that none of the prohibited post-attack outcome variables are present.

    Raises
    ------
    ValueError
        If any banned leakage column is detected.
    """
    detected_leaks: Set[str] = set(columns).intersection(set(BANNED_LEAKAGE_COLUMNS))
    if detected_leaks:
        raise ValueError(
            f"DATA LEAKAGE DETECTED: Features contain post-attack outcome variables: {detected_leaks}. "
            f"Banned columns: {BANNED_LEAKAGE_COLUMNS}"
        )


def prepare_target(df: pd.DataFrame) -> pd.Series:
    """
    Extract and consolidate target attack type:
    Retains top attack categories and merges rarest into 'Other'.
    """
    if TARGET_COLUMN not in df.columns:
        raise KeyError(f"Target column '{TARGET_COLUMN}' not found in DataFrame.")

    target = df[TARGET_COLUMN].fillna("Other").astype(str).str.strip()
    target_clean = target.apply(lambda x: x if x in TOP_ATTACK_TYPES else "Other")
    return target_clean


def build_pre_attack_features(
    df: pd.DataFrame,
    check_leakage: bool = True,
) -> pd.DataFrame:
    """
    Extract feature subset strictly limited to pre-attack operational data.

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame.
    check_leakage : bool
        Whether to run assertion against banned leakage variables.

    Returns
    -------
    pd.DataFrame
        DataFrame containing ONLY pre-attack feature columns.
    """
    if check_leakage:
        assert_no_leakage(list(df.columns))

    cols_to_use = [c for c in ALLOWED_PRE_ATTACK_FEATURES if c in df.columns]

    X = df[cols_to_use].copy()

    # Fill text columns with Unknown
    text_cols = ["region_txt", "country_txt", "provstate", "targtype1_txt", "weaptype1_txt", "gname"]
    for col in text_cols:
        if col in X.columns:
            X[col] = X[col].fillna("Unknown").astype(str).str.strip()

    # Missing coordinate indicator
    if "latitude" in X.columns and "longitude" in X.columns:
        X["coord_missing"] = (X["latitude"].isna() | X["longitude"].isna()).astype(int)

    return X


def create_preprocessor() -> ColumnTransformer:
    """
    Construct a scikit-learn ColumnTransformer that handles:
    - Categorical variables: OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    - Numeric variables (year, lat, lon): SimpleImputer + StandardScaler
    - Missing coordinate flag: passthrough
    """
    categorical_cols = [
        "region_txt",
        "country_txt",
        "provstate",
        "targtype1_txt",
        "weaptype1_txt",
        "gname",
    ]
    numeric_cols = ["iyear", "latitude", "longitude"]

    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False, max_categories=100)),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, numeric_cols),
            ("cat", cat_pipeline, categorical_cols),
            ("flag", "passthrough", ["coord_missing"]),
        ],
        remainder="drop",
    )
    return preprocessor


def get_temporal_split(
    df: pd.DataFrame,
    train_max_year: int = TRAIN_MAX_YEAR,
    test_min_year: int = TEST_MIN_YEAR,
    test_max_year: int = TEST_MAX_YEAR,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Partition dataset strictly along temporal boundaries to prevent future data leakage:
    - Train: iyear <= train_max_year (e.g. 1970–2012)
    - Test: test_min_year <= iyear <= test_max_year (e.g. 2013–2017)

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned GTD DataFrame.

    Returns
    -------
    Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]
        (X_train, y_train, X_test, y_test)
    """
    train_mask = df["iyear"] <= train_max_year
    test_mask = (df["iyear"] >= test_min_year) & (df["iyear"] <= test_max_year)

    df_train = df[train_mask].copy()
    df_test = df[test_mask].copy()

    logger.info(
        "Temporal split applied: Train=%d incidents (<= %d), Test=%d incidents (%d-%d)",
        len(df_train),
        train_max_year,
        len(df_test),
        test_min_year,
        test_max_year,
    )

    y_train = prepare_target(df_train)
    y_test = prepare_target(df_test)

    # Exclude target and banned columns from X
    df_train_features = df_train.drop(columns=[TARGET_COLUMN], errors="ignore")
    df_test_features = df_test.drop(columns=[TARGET_COLUMN], errors="ignore")

    X_train = build_pre_attack_features(df_train_features, check_leakage=False)
    X_test = build_pre_attack_features(df_test_features, check_leakage=False)

    # Strict leakage validation on resulting matrices
    assert_no_leakage(list(X_train.columns))
    assert_no_leakage(list(X_test.columns))

    return X_train, y_train, X_test, y_test

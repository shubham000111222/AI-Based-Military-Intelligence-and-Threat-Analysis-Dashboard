"""
Unit tests for data_loader.py cleaning functions and pipeline rules.
Verifies:
1. Handling of imonth/iday == 0.
2. Keeping rows with missing lat/long for models while setting has_coordinates flag.
3. Filling nkill/nwound NaN with 0 for totals while keeping casualties_known flag.
4. Normalizing group names and resolving known aliases.
5. Collapsing rare categories to 'Other'.
6. Full end-to-end cleaning pipeline execution.
"""

import pandas as pd

from src.config import OTHER_CATEGORY_LABEL, UNKNOWN_GROUP_NAME
from src.data_loader import (
    clean_casualties,
    clean_coordinates,
    clean_data,
    clean_dates,
    collapse_rare_categories,
    normalise_group_names,
)


def test_clean_dates_zero_handling(sample_raw_df):
    """Rule 1: Verify imonth == 0 and iday == 0 are imputed safely into approx_date."""
    df_cleaned = clean_dates(sample_raw_df)

    # approx_date column must exist and be datetime
    assert "approx_date" in df_cleaned.columns
    assert pd.api.types.is_datetime64_any_dtype(df_cleaned["approx_date"])

    # No NaT values should remain in approx_date
    assert df_cleaned["approx_date"].isna().sum() == 0

    # date_known flag must be False when imonth == 0 or iday == 0
    row_0 = df_cleaned.iloc[0]  # month=0, day=0
    assert row_0["date_known"] is False or row_0["date_known"] == 0
    assert row_0["approx_date"].year == 1985
    assert row_0["approx_date"].month == 1
    assert row_0["approx_date"].day == 1

    row_3 = df_cleaned.iloc[3]  # month=9, day=11
    assert row_3["date_known"] is True or row_3["date_known"] == 1
    assert row_3["approx_date"].month == 9
    assert row_3["approx_date"].day == 11


def test_clean_casualties_rules(sample_raw_df):
    """Rule 3: Fill nkill/nwound NaN with 0 only in casualty totals while keeping casualties_known flag."""
    df_cleaned = clean_casualties(sample_raw_df)

    # Check existence of required casualty metrics
    assert "ncasualty" in df_cleaned.columns
    assert "casualties_known" in df_cleaned.columns

    # Row 1 had nkill=NaN and nwound=NaN -> casualties_known must be False
    assert df_cleaned.iloc[1]["casualties_known"] == False  # noqa: E712
    # In casualty total it should be 0.0
    assert df_cleaned.iloc[1]["nkill"] == 0.0
    assert df_cleaned.iloc[1]["nwound"] == 0.0
    assert df_cleaned.iloc[1]["ncasualty"] == 0.0

    # Row 0 had nkill=2.0 and nwound=5.0 -> casualties_known is True, total is 7.0
    assert df_cleaned.iloc[0]["casualties_known"] == True  # noqa: E712
    assert df_cleaned.iloc[0]["ncasualty"] == 7.0

    # Row 3 had nkill=1.0 and nwound=NaN -> casualties_known is True (at least one known)
    assert df_cleaned.iloc[3]["casualties_known"] == True  # noqa: E712
    assert df_cleaned.iloc[3]["ncasualty"] == 1.0


def test_clean_coordinates_retention(sample_raw_df):
    """Rule 2: Keep rows with missing lat/long for models and flag them for map views."""
    df_cleaned = clean_coordinates(sample_raw_df)

    # Row count must NOT decrease (no dropping for models)
    assert len(df_cleaned) == len(sample_raw_df)

    assert "has_coordinates" in df_cleaned.columns
    # Row 2 had NaN lat/long -> has_coordinates must be False
    assert df_cleaned.iloc[2]["has_coordinates"] == False  # noqa: E712
    # Row 0 had valid lat/long -> has_coordinates must be True
    assert df_cleaned.iloc[0]["has_coordinates"] == True  # noqa: E712


def test_clean_coordinates_out_of_bounds():
    """Verify out-of-bound coordinates are invalidated."""
    df_invalid = pd.DataFrame({
        "latitude": [105.0, -95.0, 45.0],
        "longitude": [200.0, -190.0, 10.0],
    })
    df_cleaned = clean_coordinates(df_invalid)
    assert df_cleaned.iloc[0]["has_coordinates"] == False  # noqa: E712
    assert df_cleaned.iloc[1]["has_coordinates"] == False  # noqa: E712
    assert df_cleaned.iloc[2]["has_coordinates"] == True  # noqa: E712


def test_normalise_group_names(sample_raw_df):
    """Rule 4: Strip whitespace, map aliases, and normalize Unknown."""
    df_cleaned = normalise_group_names(sample_raw_df)

    # "  Taliban  " -> "Taliban"
    assert df_cleaned.iloc[0]["gname"] == "Taliban"

    # "ISIL" -> "Islamic State of Iraq and the Levant (ISIL)"
    assert df_cleaned.iloc[2]["gname"] == "Islamic State of Iraq and the Levant (ISIL)"

    # Empty string -> UNKNOWN_GROUP_NAME
    assert df_cleaned.iloc[5]["gname"] == UNKNOWN_GROUP_NAME


def test_collapse_rare_categories(sample_raw_df):
    """Rule 5: Rare categories collapsed to 'Other'."""
    # In sample_raw_df, "Very Rare Exotic Attack 1" has frequency 1/7 (~14%).
    # Using min_freq=0.20 will trigger collapsing
    df_collapsed = collapse_rare_categories(
        sample_raw_df,
        columns=["attacktype1_txt", "targtype1_txt", "weaptype1_txt"],
        min_freq=0.20,
    )

    assert OTHER_CATEGORY_LABEL in df_collapsed["attacktype1_txt"].values
    assert df_collapsed.iloc[5]["attacktype1_txt"] == OTHER_CATEGORY_LABEL
    assert df_collapsed.iloc[5]["targtype1_txt"] == OTHER_CATEGORY_LABEL
    assert df_collapsed.iloc[5]["weaptype1_txt"] == OTHER_CATEGORY_LABEL


def test_full_cleaning_pipeline(sample_raw_df):
    """End-to-end cleaning pipeline validation."""
    df_clean = clean_data(sample_raw_df, is_raw=True, collapse_rare=True)

    # Length preserved
    assert len(df_clean) == len(sample_raw_df)

    # Key columns present
    for col in ["ncasualty", "casualties_known", "has_coordinates", "approx_date"]:
        assert col in df_clean.columns

    # No negative casualties
    assert (df_clean["nkill"] >= 0).all()
    assert (df_clean["nwound"] >= 0).all()
    assert (df_clean["ncasualty"] >= 0).all()

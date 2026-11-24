"""
Data loading and cleaning pipeline for the Global Terrorism Database (GTD).
Handles schema filtering, date normalization, casualty imputation,
coordinate verification, group name standardization, and rare category collapsing.
"""

import logging
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import pandas as pd

from src.config import (
    GROUP_NORMALIZATION_MAP,
    KEEP_COLUMNS,
    MISSING_YEAR,
    OTHER_CATEGORY_LABEL,
    PROCESSED_DATA_PATH,
    RARE_CATEGORY_MIN_FREQ,
    RAW_DATA_PATH,
    RAW_ENCODING,
    RAW_LOW_MEMORY,
    UNKNOWN_GROUP_NAME,
)

logger = logging.getLogger(__name__)


def load_raw_data(
    filepath: Union[str, Path] = RAW_DATA_PATH,
    encoding: str = RAW_ENCODING,
    low_memory: bool = RAW_LOW_MEMORY,
) -> pd.DataFrame:
    """
    Load raw GTD CSV dataset using prescribed encoding and column filtering.

    Parameters
    ----------
    filepath : str or Path
        Path to the raw CSV file.
    encoding : str
        Character encoding (default ISO-8859-1 for GTD).
    low_memory : bool
        Pandas low_memory flag.

    Returns
    -------
    pd.DataFrame
        DataFrame containing filtered GTD columns.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(
            f"Raw GTD dataset not found at '{path}'. "
            "Please download the Kaggle GTD dataset to data/raw/globalterrorismdb_0718dist.csv"
        )

    logger.info("Loading raw GTD dataset from %s", path)
    # Read only requested columns if present in raw file
    df_preview = pd.read_csv(path, nrows=2, encoding=encoding, low_memory=low_memory)
    available_cols = [c for c in KEEP_COLUMNS if c in df_preview.columns]

    df = pd.read_csv(
        path,
        usecols=available_cols,
        encoding=encoding,
        low_memory=low_memory,
    )
    logger.info("Loaded %d raw rows across %d columns", len(df), len(df.columns))
    return df


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle GTD temporal anomalies:
    - imonth == 0: unknown month (imputed to 1 for calendar indexing)
    - iday == 0: unknown day (imputed to 1 for calendar indexing)
    - Generates approx_date (datetime) and date_known flag.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with iyear, imonth, iday.

    Returns
    -------
    pd.DataFrame
        DataFrame with cleaned date columns and approx_date.
    """
    df = df.copy()

    # Ensure integer representations
    df["iyear"] = pd.to_numeric(df["iyear"], errors="coerce").fillna(1970).astype(int)
    df["imonth"] = pd.to_numeric(df["imonth"], errors="coerce").fillna(0).astype(int)
    df["iday"] = pd.to_numeric(df["iday"], errors="coerce").fillna(0).astype(int)

    # Flag whether exact calendar date is verified
    df["date_known"] = (df["imonth"] > 0) & (df["iday"] > 0)

    # Impute missing month/day for approximate timeline sequencing
    imputed_month = df["imonth"].apply(lambda m: 1 if m <= 0 or m > 12 else m)
    imputed_day = df["iday"].apply(lambda d: 1 if d <= 0 or d > 31 else d)

    date_str = (
        df["iyear"].astype(str)
        + "-"
        + imputed_month.astype(str).str.zfill(2)
        + "-"
        + imputed_day.astype(str).str.zfill(2)
    )

    df["approx_date"] = pd.to_datetime(date_str, errors="coerce")
    # Fallback to year-only if month/day combination was invalid (e.g. Feb 30)
    invalid_mask = df["approx_date"].isna()
    if invalid_mask.any():
        fallback_str = df.loc[invalid_mask, "iyear"].astype(str) + "-01-01"
        df.loc[invalid_mask, "approx_date"] = pd.to_datetime(fallback_str, errors="coerce")

    return df


def clean_casualties(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle casualty data with strict fidelity:
    - Keep track of whether casualties were known/reported via 'casualties_known' flag
    - Fill NaN with 0 only in numeric casualty totals (nkill, nwound, ncasualty)
    - Ensure non-negative casualty numbers.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with sanitized casualty columns and flags.
    """
    df = df.copy()

    # Record whether casualty information was explicitly reported
    # True if either nkill or nwound is documented; False if both are NaN
    nkill_raw = pd.to_numeric(df["nkill"], errors="coerce") if "nkill" in df.columns else pd.Series(np.nan, index=df.index)
    nwound_raw = pd.to_numeric(df["nwound"], errors="coerce") if "nwound" in df.columns else pd.Series(np.nan, index=df.index)

    df["casualties_known"] = nkill_raw.notna() | nwound_raw.notna()
    df["nkill_known"] = nkill_raw.notna()
    df["nwound_known"] = nwound_raw.notna()

    # Fill NaN with 0 for numerical casualty totals
    df["nkill"] = nkill_raw.fillna(0.0).clip(lower=0.0)
    df["nwound"] = nwound_raw.fillna(0.0).clip(lower=0.0)
    df["ncasualty"] = df["nkill"] + df["nwound"]

    return df


def clean_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean latitude and longitude:
    - Retain rows with missing lat/long for downstream ML models.
    - Add 'has_coordinates' boolean flag for map filtering.
    - Check coordinate precision (e.g. integer rounding indicating approximate centroids).
    - Nullify out-of-bound coordinates (-90 <= lat <= 90, -180 <= lon <= 180).

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with validated coordinates and precision indicators.
    """
    df = df.copy()

    lat = pd.to_numeric(df["latitude"], errors="coerce") if "latitude" in df.columns else pd.Series(np.nan, index=df.index)
    lon = pd.to_numeric(df["longitude"], errors="coerce") if "longitude" in df.columns else pd.Series(np.nan, index=df.index)

    # Invalidate coordinates that fall outside legal spherical bounds
    invalid_bounds = (lat < -90.0) | (lat > 90.0) | (lon < -180.0) | (lon > 180.0)
    lat = lat.mask(invalid_bounds, np.nan)
    lon = lon.mask(invalid_bounds, np.nan)

    df["latitude"] = lat
    df["longitude"] = lon
    df["has_coordinates"] = df["latitude"].notna() & df["longitude"].notna()

    # Precision indicator: coordinates that are exact integers usually represent city/district centroids
    is_integer_lat = (df["latitude"].dropna() % 1 == 0)
    is_integer_lon = (df["longitude"].dropna() % 1 == 0)
    df["coord_is_approx_centroid"] = False
    valid_coord_idx = df[df["has_coordinates"]].index
    df.loc[valid_coord_idx, "coord_is_approx_centroid"] = (
        is_integer_lat.reindex(valid_coord_idx, fill_value=False)
        & is_integer_lon.reindex(valid_coord_idx, fill_value=False)
    )

    return df


def normalise_group_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize terrorist group names:
    - Strip trailing/leading whitespace and standardize case formatting.
    - Map known aliases (e.g. ISIS, ISIL, Daesh -> Islamic State of Iraq and the Levant (ISIL)).
    - Normalize secondary and tertiary claim columns (gname2, gname3).
    - Ensure 'Unknown' is assigned when empty or null.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized group names.
    """
    df = df.copy()

    def _clean_str_series(series: pd.Series) -> pd.Series:
        cleaned = series.fillna("").astype(str).str.strip()
        cleaned = cleaned.replace({"": UNKNOWN_GROUP_NAME, "nan": UNKNOWN_GROUP_NAME, "None": UNKNOWN_GROUP_NAME})
        # Map known aliases
        for alias, target in GROUP_NORMALIZATION_MAP.items():
            cleaned = cleaned.replace(alias, target)
        return cleaned

    if "gname" in df.columns:
        df["gname"] = _clean_str_series(df["gname"])

    for col in ["gname2", "gname3"]:
        if col in df.columns:
            s = df[col].fillna("").astype(str).str.strip()
            df[col] = s.replace({"": None, "nan": None, "None": None})
            for alias, target in GROUP_NORMALIZATION_MAP.items():
                df[col] = df[col].replace(alias, target)

    return df


def collapse_rare_categories(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    min_freq: float = RARE_CATEGORY_MIN_FREQ,
) -> pd.DataFrame:
    """
    Collapse long-tail rare categories in categorical variables to 'Other'.
    Protects downstream models from severe high-cardinality noise and unseen class issues.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    columns : list of str, optional
        Columns to process. Defaults to attacktype1_txt, targtype1_txt, weaptype1_txt.
    min_freq : float
        Minimum relative frequency threshold. Classes below this share are mapped to 'Other'.

    Returns
    -------
    pd.DataFrame
        DataFrame with collapsed categories.
    """
    df = df.copy()
    if columns is None:
        columns = ["attacktype1_txt", "targtype1_txt", "weaptype1_txt"]

    total_rows = len(df)
    if total_rows == 0:
        return df

    for col in columns:
        if col not in df.columns:
            continue

        # Standardize strings
        df[col] = df[col].fillna(OTHER_CATEGORY_LABEL).astype(str).str.strip()
        counts = df[col].value_counts()
        freqs = counts / total_rows

        # Rare classes below threshold
        rare_classes = freqs[freqs < min_freq].index.tolist()
        # Keep 'Unknown' if already present, otherwise collapse
        df[col] = df[col].apply(lambda x: OTHER_CATEGORY_LABEL if x in rare_classes else x)

    return df


def clean_text_and_categorical(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values and standardize text columns:
    - country_txt, region_txt, provstate, city
    - success, suicide binary casting
    - summary text sanitization

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        Sanitized DataFrame.
    """
    df = df.copy()

    for col in ["country_txt", "region_txt"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    for col in ["provstate", "city"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    for col in ["success", "suicide"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int).clip(0, 1)

    if "summary" in df.columns:
        df["summary"] = df["summary"].fillna("").astype(str).str.strip()
        df["has_summary"] = df["summary"].str.len() > 10
    else:
        df["summary"] = ""
        df["has_summary"] = False

    return df


def clean_data(
    df: pd.DataFrame,
    is_raw: bool = True,
    collapse_rare: bool = True,
) -> pd.DataFrame:
    """
    Execute full data cleaning pipeline for the GTD dataset.

    Pipeline stages:
    1. Schema alignment (keep only designated columns)
    2. Date sanitization and approx_date generation
    3. Casualty processing and known-status flagging
    4. Coordinate validation and bounds verification
    5. Group name normalization
    6. Text and binary attribute cleaning
    7. Rare category collapsing

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    is_raw : bool
        If True, restricts to KEEP_COLUMNS present.
    collapse_rare : bool
        Whether to collapse rare categories to 'Other'.

    Returns
    -------
    pd.DataFrame
        Cleaned, type-optimized DataFrame.
    """
    logger.info("Executing GTD cleaning pipeline on %d rows", len(df))

    # 1. Filter columns
    if is_raw:
        cols_to_use = [c for c in KEEP_COLUMNS if c in df.columns]
        df_clean = df[cols_to_use].copy()
    else:
        df_clean = df.copy()

    # 2. Date sanitization
    df_clean = clean_dates(df_clean)

    # 3. Casualty sanitization
    df_clean = clean_casualties(df_clean)

    # 4. Coordinate validation
    df_clean = clean_coordinates(df_clean)

    # 5. Group normalization
    df_clean = normalise_group_names(df_clean)

    # 6. Text and categorical fields
    df_clean = clean_text_and_categorical(df_clean)

    # 7. Rare categories
    if collapse_rare:
        df_clean = collapse_rare_categories(df_clean)

    logger.info("Cleaning pipeline complete. Processed %d records.", len(df_clean))
    return df_clean


def generate_synthetic_gtd(
    n_records: int = 5000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic Global Terrorism Database records matching the schema,
    distributions, and known historical characteristics (including the missing 1993 gap).
    Essential for CI testing, rapid test execution, and environments where the
    160MB Kaggle CSV is not yet placed in data/raw/.

    Parameters
    ----------
    n_records : int
        Number of synthetic incidents to generate.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Synthetic raw-like GTD DataFrame.
    """
    rng = np.random.default_rng(seed)

    # Years 1970 to 2017 excluding 1993
    allowed_years = [y for y in range(1970, 2018) if y != MISSING_YEAR]
    # Weight modern years higher reflecting historical GTD record distribution
    weights = np.linspace(1, 10, len(allowed_years))
    weights /= weights.sum()
    years = rng.choice(allowed_years, size=n_records, p=weights)

    # Months (0 to 12, with ~2% unknown 0)
    month_choices = [0] + list(range(1, 13))
    month_p = [0.02] + [0.98 / 12] * 12
    months = rng.choice(month_choices, size=n_records, p=month_p)

    # Days (0 to 31, with ~3% unknown 0)
    day_choices = [0] + list(range(1, 29))
    day_p = [0.03] + [0.97 / 28] * 28
    days = rng.choice(day_choices, size=n_records, p=day_p)

    # Regions & Countries
    regions_countries = [
        ("Middle East & North Africa", ["Iraq", "Syria", "Yemen", "Egypt", "Libya", "Algeria"]),
        ("South Asia", ["Afghanistan", "Pakistan", "India", "Bangladesh", "Sri Lanka"]),
        ("Sub-Saharan Africa", ["Nigeria", "Somalia", "Kenya", "Democratic Republic of the Congo", "Mali"]),
        ("Western Europe", ["United Kingdom", "Spain", "France", "Germany", "Northern Ireland"]),
        ("South America", ["Colombia", "Peru", "Chile", "El Salvador", "Guatemala"]),
        ("Southeast Asia", ["Philippines", "Thailand", "Indonesia", "Myanmar"]),
        ("North America", ["United States", "Canada"]),
        ("Eastern Europe", ["Russia", "Ukraine"]),
    ]
    region_idx = rng.choice(len(regions_countries), size=n_records, p=[0.30, 0.28, 0.15, 0.08, 0.08, 0.05, 0.03, 0.03])
    region_list = []
    country_list = []
    for idx in region_idx:
        reg, countries = regions_countries[idx]
        region_list.append(reg)
        country_list.append(rng.choice(countries))

    # Cities and provstates
    provstates = ["Capital District", "Northern Province", "Southern State", "Eastern Frontier", "Western Sector", "Unknown"]
    cities = ["Baghdad", "Kabul", "Mogadishu", "Belfast", "Medellin", "Peshawar", "Karachi", "Paris", "London", "Unknown"]
    sample_provstates = rng.choice(provstates, size=n_records)
    sample_cities = rng.choice(cities, size=n_records)

    # Latitudes and longitudes with ~12% missing (real GTD has ~8-12% missing)
    has_coords = rng.choice([True, False], size=n_records, p=[0.88, 0.12])
    lats = []
    lons = []
    for hc in has_coords:
        if hc:
            lats.append(round(rng.uniform(-35.0, 55.0), 4))
            lons.append(round(rng.uniform(-80.0, 110.0), 4))
        else:
            lats.append(np.nan)
            lons.append(np.nan)

    # Attack types
    attack_types = [
        "Bombing/Explosion",
        "Armed Assault",
        "Assassination",
        "Hostage Taking (Kidnapping)",
        "Facility/Infrastructure Attack",
        "Unarmed Assault",
        "Hijacking",
        "Hostage Taking (Barricade Incident)",
        "Unknown",
    ]
    attack_p = [0.48, 0.24, 0.10, 0.07, 0.05, 0.02, 0.01, 0.01, 0.02]
    sample_attacks = rng.choice(attack_types, size=n_records, p=attack_p)

    # Target types
    target_types = [
        "Private Citizens & Property",
        "Military",
        "Police",
        "Government (General)",
        "Business",
        "Transportation",
        "Religious Figures/Institutions",
        "Educational Institution",
        "Telecommunication",
        "Journalists & Media",
    ]
    targ_p = [0.26, 0.20, 0.18, 0.14, 0.08, 0.05, 0.04, 0.02, 0.01, 0.02]
    sample_targets = rng.choice(target_types, size=n_records, p=targ_p)

    # Weapon types
    weapon_types = [
        "Explosives",
        "Firearms",
        "Incendiary",
        "Melee",
        "Chemical",
        "Unknown",
    ]
    weap_p = [0.52, 0.36, 0.05, 0.03, 0.01, 0.03]
    sample_weapons = rng.choice(weapon_types, size=n_records, p=weap_p)

    # Perpetrator Groups (with ~45% Unknown representing historical GTD unclaimed incidents)
    group_choices = [
        "Unknown",
        "Taliban",
        "Islamic State of Iraq and the Levant (ISIL)",
        "Al-Shabaab",
        "Boko Haram",
        "Communist Party of India - Maoist (CPI-Maoist)",
        "New People's Army (NPA)",
        "Tehrik-i-Taliban Pakistan (TTP)",
        "Farabundo Marti National Liberation Front (FMLN)",
        "Irish Republican Army (IRA)",
        "Revolutionary Armed Forces of Colombia (FARC)",
        "Kurdistan Workers' Party (PKK)",
        "Al-Qaida",
        "Basque Fatherland and Freedom (ETA)",
    ]
    grp_p = [0.45, 0.10, 0.08, 0.06, 0.05, 0.04, 0.04, 0.03, 0.03, 0.03, 0.03, 0.02, 0.02, 0.02]
    sample_groups = rng.choice(group_choices, size=n_records, p=grp_p)

    # Secondary claims
    gname2_list = [rng.choice(["Al-Qaida in Iraq", "Jundallah", None], p=[0.05, 0.05, 0.90]) for _ in range(n_records)]
    gname3_list = [None] * n_records

    # Casualties: nkill & nwound with ~8% unrecorded (NaN)
    has_nkill = rng.choice([True, False], size=n_records, p=[0.92, 0.08])
    has_nwound = rng.choice([True, False], size=n_records, p=[0.88, 0.12])

    # Log-normal distribution for fatalities
    nkill_vals = rng.exponential(scale=2.2, size=n_records).astype(int)
    nwound_vals = rng.exponential(scale=3.8, size=n_records).astype(int)

    nkill_series = [float(nkill_vals[i]) if has_nkill[i] else np.nan for i in range(n_records)]
    nwound_series = [float(nwound_vals[i]) if has_nwound[i] else np.nan for i in range(n_records)]

    # Success and suicide flags
    success = rng.choice([1, 0], size=n_records, p=[0.88, 0.12])
    suicide = rng.choice([0, 1], size=n_records, p=[0.95, 0.05])

    # Summaries
    summaries = [
        f"Incident reported in {country_list[i]}: {sample_attacks[i]} targeting {sample_targets[i]} by {sample_groups[i]}."
        if rng.random() > 0.15
        else ""
        for i in range(n_records)
    ]

    raw_dict = {
        "iyear": years,
        "imonth": months,
        "iday": days,
        "country_txt": country_list,
        "region_txt": region_list,
        "provstate": sample_provstates,
        "city": sample_cities,
        "latitude": lats,
        "longitude": lons,
        "attacktype1_txt": sample_attacks,
        "targtype1_txt": sample_targets,
        "weaptype1_txt": sample_weapons,
        "gname": sample_groups,
        "gname2": gname2_list,
        "gname3": gname3_list,
        "nkill": nkill_series,
        "nwound": nwound_series,
        "success": success,
        "suicide": suicide,
        "summary": summaries,
    }

    return pd.DataFrame(raw_dict)


def load_dataset(
    filepath: Union[str, Path] = PROCESSED_DATA_PATH,
    fallback_to_synthetic: bool = True,
) -> pd.DataFrame:
    """
    Primary accessor for the cleaned GTD dataset.
    Loads the parquet file from disk. If the parquet file is not yet built:
    - Tries loading raw CSV and cleaning it.
    - If raw CSV is absent, generates synthetic data and saves processed parquet
      so that all dashboard pages and tests operate seamlessly.

    Parameters
    ----------
    filepath : str or Path
        Target processed parquet path.
    fallback_to_synthetic : bool
        If True and no raw file exists, generates synthetic data for development.

    Returns
    -------
    pd.DataFrame
        Cleaned, ready-to-analyze GTD DataFrame.
    """
    path = Path(filepath)
    if path.exists():
        logger.info("Loading processed parquet from %s", path)
        return pd.read_parquet(path)

    # Check if raw data exists to build it
    if RAW_DATA_PATH.exists():
        logger.info("Raw data found. Building processed dataset...")
        df_raw = load_raw_data(RAW_DATA_PATH)
        df_clean = clean_data(df_raw, is_raw=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        df_clean.to_parquet(path, index=False)
        return df_clean

    if fallback_to_synthetic:
        logger.warning(
            "Neither processed parquet nor raw CSV found at '%s'. "
            "Generating 10,000 synthetic GTD records for development and testing.",
            RAW_DATA_PATH,
        )
        df_synth_raw = generate_synthetic_gtd(n_records=10000, seed=42)
        df_clean = clean_data(df_synth_raw, is_raw=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        df_clean.to_parquet(path, index=False)
        return df_clean

    raise FileNotFoundError(
        f"GTD data file not found at '{path}' and raw dataset missing at '{RAW_DATA_PATH}'."
    )

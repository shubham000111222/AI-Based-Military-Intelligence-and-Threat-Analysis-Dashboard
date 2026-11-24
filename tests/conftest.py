"""
Pytest fixtures for GTD testing.
Provides synthetic test DataFrames with verified edge cases:
- 0 imonth / 0 iday
- Missing coordinates and boundary violations
- Missing casualties (NaN nkill / nwound)
- Group name variations and aliases
- Rare categorical classes
"""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_raw_df() -> pd.DataFrame:
    """
    Construct a deterministic synthetic DataFrame containing all key edge cases.
    """
    return pd.DataFrame({
        "iyear": [1985, 1990, 1995, 2001, 2010, 2015, 2017],
        "imonth": [0, 5, 12, 9, 0, 7, 11],       # Month 0 edge cases
        "iday": [0, 0, 25, 11, 15, 0, 28],      # Day 0 edge cases
        "country_txt": ["United States", "United Kingdom", "Iraq", "Colombia", "Afghanistan", "Nigeria", "Syria"],
        "region_txt": [
            "North America",
            "Western Europe",
            "Middle East & North Africa",
            "South America",
            "South Asia",
            "Sub-Saharan Africa",
            "Middle East & North Africa",
        ],
        "provstate": ["New York", "Northern Ireland", "Baghdad", "Antioquia", "Kabul", "Borno", "Aleppo"],
        "city": ["New York City", "Belfast", "Baghdad", "Medellin", "Kabul", "Maiduguri", "Aleppo"],
        "latitude": [40.7128, 54.5973, np.nan, 6.2442, 34.5553, np.nan, 36.2021],  # Missing lat
        "longitude": [-74.0060, -5.9301, np.nan, -75.5812, 69.2075, np.nan, 37.1343], # Missing lon
        "attacktype1_txt": [
            "Bombing/Explosion",
            "Bombing/Explosion",
            "Armed Assault",
            "Assassination",
            "Bombing/Explosion",
            "Very Rare Exotic Attack 1",  # Rare attack type
            "Bombing/Explosion",
        ],
        "targtype1_txt": [
            "Business",
            "Police",
            "Military",
            "Government (General)",
            "Private Citizens & Property",
            "Rare Micro Target",          # Rare target type
            "Private Citizens & Property",
        ],
        "weaptype1_txt": [
            "Explosives",
            "Explosives",
            "Firearms",
            "Firearms",
            "Explosives",
            "Rare Experimental Ray",      # Rare weapon type
            "Explosives",
        ],
        "gname": [
            "  Taliban  ",               # Whitespace
            "IRA",                       # Alias
            "ISIL",                      # Alias
            "FARC",                      # Alias
            "Unknown",                   # Unknown group
            "",                          # Empty string
            "Islamic State of Iraq and the Levant (ISIL)",
        ],
        "gname2": [None, None, "Al-Qaida", None, None, None, None],
        "gname3": [None, None, None, None, None, None, None],
        "nkill": [2.0, np.nan, 10.0, 1.0, 0.0, np.nan, 4.0],  # NaN kills
        "nwound": [5.0, np.nan, 25.0, np.nan, 0.0, np.nan, 12.0], # NaN wounds
        "success": [1, 1, 1, 0, 1, 1, 1],
        "suicide": [0, 0, 1, 0, 1, 1, 0],
        "summary": [
            "A powerful explosive device detonated inside the commercial office tower.",
            "Mortar shells struck near the perimeter checkpoint in Belfast.",
            "",  # Empty summary
            "Assassination attempt targeting regional judicial magistrate.",
            "Suicide vehicle-borne improvised explosive device targeted convoy.",
            None, # Null summary
            "Coordinated explosive assault on civilian marketplace.",
        ],
    })


@pytest.fixture
def synthetic_multidecade_df() -> pd.DataFrame:
    """
    Fixture with incidents spanning decades 1970 to 2017 (missing 1993).
    """
    from src.data_loader import clean_data, generate_synthetic_gtd
    raw = generate_synthetic_gtd(n_records=300, seed=123)
    return clean_data(raw, is_raw=True)

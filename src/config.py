"""
Configuration module for the AI-Based Military Intelligence & Threat Analysis Dashboard.
Centralizes paths, column definitions, data hygiene parameters, modeling cutoffs, and UI styling.
"""

from pathlib import Path
from typing import Dict, List

# ---------------------------------------------------------------------------
# Directory Structure
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
ARTIFACTS_DIR: Path = BASE_DIR / "artifacts"
MODELS_DIR: Path = BASE_DIR / "models"
DOCS_DIR: Path = BASE_DIR / "docs"
TESTS_DIR: Path = BASE_DIR / "tests"

RAW_DATA_PATH: Path = RAW_DATA_DIR / "globalterrorismdb_0718dist.csv"
PROCESSED_DATA_PATH: Path = PROCESSED_DATA_DIR / "gtd_slim.parquet"
METRICS_JSON_PATH: Path = ARTIFACTS_DIR / "metrics.json"
EMBEDDINGS_NPY_PATH: Path = ARTIFACTS_DIR / "embeddings.npy"

# Ensure runtime directories exist
for folder in [RAW_DATA_DIR, PROCESSED_DATA_DIR, ARTIFACTS_DIR, MODELS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# GTD Data Schema & Specifications
# ---------------------------------------------------------------------------
RAW_ENCODING: str = "ISO-8859-1"
RAW_LOW_MEMORY: bool = False

# Exact 20 columns required for the slim data pipeline
KEEP_COLUMNS: List[str] = [
    "iyear",
    "imonth",
    "iday",
    "country_txt",
    "region_txt",
    "provstate",
    "city",
    "latitude",
    "longitude",
    "attacktype1_txt",
    "targtype1_txt",
    "weaptype1_txt",
    "gname",
    "gname2",
    "gname3",
    "nkill",
    "nwound",
    "success",
    "suicide",
    "summary",
]

# Explicit features banned from predictive models to prevent data leakage
BANNED_LEAKAGE_COLUMNS: List[str] = [
    "nkill",
    "nwound",
    "ncasualty",
    "success",
    "suicide",
    "summary",
    "casualties_known",
]

# Temporal boundaries
MIN_YEAR: int = 1970
MAX_YEAR: int = 2017
MISSING_YEAR: int = 1993

MISSING_YEAR_ANNOTATION: str = (
    "1993 Data Gap: Original incident records for 1993 were lost in transit by the START collection "
    "team prior to digital centralization. Only partial records were recovered and they are excluded "
    "from standard release versions."
)

# ---------------------------------------------------------------------------
# Data Hygiene & Normalization
# ---------------------------------------------------------------------------
UNKNOWN_GROUP_NAME: str = "Unknown"
OTHER_CATEGORY_LABEL: str = "Other"
RARE_CATEGORY_MIN_FREQ: float = 0.01  # Categories with frequency < 1% collapsed to Other

# Known perpetrator group aliases for standardisation
GROUP_NORMALIZATION_MAP: Dict[str, str] = {
    "Islamic State of Iraq and the Levant (ISIL)": "Islamic State of Iraq and the Levant (ISIL)",
    "Islamic State of Iraq and the Levant": "Islamic State of Iraq and the Levant (ISIL)",
    "ISIS": "Islamic State of Iraq and the Levant (ISIL)",
    "ISIL": "Islamic State of Iraq and the Levant (ISIL)",
    "Daesh": "Islamic State of Iraq and the Levant (ISIL)",
    "Al-Qaida": "Al-Qaida",
    "Al-Qaeda": "Al-Qaida",
    "Al-Qaida in Iraq": "Al-Qaida in Iraq",
    "Tehrik-i-Taliban Pakistan (TTP)": "Tehrik-i-Taliban Pakistan (TTP)",
    "Boko Haram": "Boko Haram",
    "Al-Shabaab": "Al-Shabaab",
    "Taliban": "Taliban",
    "Farabundo Marti National Liberation Front (FMLN)": "Farabundo Marti National Liberation Front (FMLN)",
    "Irish Republican Army (IRA)": "Irish Republican Army (IRA)",
    "New People's Army (NPA)": "New People's Army (NPA)",
    "Revolutionary Armed Forces of Colombia (FARC)": "Revolutionary Armed Forces of Colombia (FARC)",
    "Shining Path (SL)": "Shining Path (SL)",
    "Kurdistan Workers' Party (PKK)": "Kurdistan Workers' Party (PKK)",
    "Basque Fatherland and Freedom (ETA)": "Basque Fatherland and Freedom (ETA)",
    "Liberation Tigers of Tamil Eelam (LTTE)": "Liberation Tigers of Tamil Eelam (LTTE)",
}

# ---------------------------------------------------------------------------
# Modeling & Evaluation Parameters
# ---------------------------------------------------------------------------
TRAIN_MAX_YEAR: int = 2012
TEST_MIN_YEAR: int = 2013
TEST_MAX_YEAR: int = 2017
RANDOM_SEED: int = 42

# Default Risk Index Component Weights
DEFAULT_RISK_WEIGHTS: Dict[str, float] = {
    "log_incidents": 0.30,
    "log_casualties": 0.30,
    "trend_slope": 0.20,
    "mass_casualty_ratio": 0.20,
}

# Mass casualty definition: incident with >= 10 casualties
MASS_CASUALTY_THRESHOLD: int = 10

# ---------------------------------------------------------------------------
# LLM / Gemini Settings
# ---------------------------------------------------------------------------
GEMINI_MODEL: str = "gemini-2.5-flash"
GEMINI_TEMPERATURE: float = 0.2

# ---------------------------------------------------------------------------
# Visual Styling & Branding
# ---------------------------------------------------------------------------
THEME_COLORS = {
    "primary": "#D32F2F",       # Tactical deep crimson
    "secondary": "#1A1D24",     # Slate dark background card
    "background": "#0E1117",    # Deep terminal obsidian
    "text": "#E0E0E0",          # Crisp reading off-white
    "accent_cyan": "#00E5FF",    # Radar/cyan highlight
    "accent_gold": "#FFD600",    # Warning/amber highlight
    "accent_green": "#00E676",   # Low risk / success green
    "danger": "#FF1744",        # Critical threat
    "missing_annotation": "#FF9100", # Visual gap marker
}

# ---------------------------------------------------------------------------
# Project Framing & Ethical Disclaimer
# ---------------------------------------------------------------------------
ETHICAL_DISCLAIMER: str = (
    "EDUCATIONAL & RESEARCH USE ONLY: This dashboard is a historical, academic retrospective "
    "intelligence analytics platform engineered for statistical pattern exploration, risk indexing, "
    "and machine learning evaluation on historical Global Terrorism Database (GTD) data (1970–2017). "
    "It is NOT an operational targeting tool, live tactical surveillance system, or predictive kinetic feed. "
    "All outputs represent historical aggregations and statistical models subject to historical recording biases."
)

"""
Page 16: Raw Intelligence Data Explorer
Interactive tabular inspection of the Global Terrorism Database with multi-column filtering,
full-text search, customizable column projection, paginated browsing, and filtered CSV export.
"""

import math

import pandas as pd
import streamlit as st

from src.config import (
    ETHICAL_DISCLAIMER,
)
from src.data_loader import load_dataset

st.set_page_config(
    page_title="Data Explorer | AI Threat Intelligence",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Historical Intelligence Data Explorer")
st.caption(
    "Interactive tabular inspection of the Global Terrorism Database (GTD) historical archive (1970–2017). "
    "Filter across geopolitical dimensions, execute text searches, customize column projection, and export slices to CSV."
)

st.warning(f"⚖️ **Analytical & Historical Notice**: {ETHICAL_DISCLAIMER}")


@st.cache_data
def get_data():
    return load_dataset()


df = get_data()

# ---------------------------------------------------------------------------
# Sidebar Filters & Search
# ---------------------------------------------------------------------------
st.sidebar.header("🎯 Exploration Filters")

# Year Range Slider
min_yr = int(df["iyear"].min()) if "iyear" in df.columns else 1970
max_yr = int(df["iyear"].max()) if "iyear" in df.columns else 2017

selected_years = st.sidebar.slider(
    "Temporal Range",
    min_value=min_yr,
    max_value=max_yr,
    value=(min_yr, max_yr),
)

# Region Filter
all_regions = sorted(df["region_txt"].dropna().unique().tolist()) if "region_txt" in df.columns else []
selected_regions = st.sidebar.multiselect("Geographic Theatres", options=all_regions, default=[])

# Country Filter (conditional on selected regions if chosen)
if selected_regions:
    country_pool = df[df["region_txt"].isin(selected_regions)]["country_txt"].dropna().unique().tolist()
else:
    country_pool = df["country_txt"].dropna().unique().tolist() if "country_txt" in df.columns else []
selected_countries = st.sidebar.multiselect("Countries", options=sorted(country_pool), default=[])

# Attack Type Filter
all_attacks = sorted(df["attacktype1_txt"].dropna().unique().tolist()) if "attacktype1_txt" in df.columns else []
selected_attacks = st.sidebar.multiselect("Attack Modalities", options=all_attacks, default=[])

# Target Type Filter
all_targets = sorted(df["targtype1_txt"].dropna().unique().tolist()) if "targtype1_txt" in df.columns else []
selected_targets = st.sidebar.multiselect("Target Sectors", options=all_targets, default=[])

# Weapon Type Filter
all_weapons = sorted(df["weaptype1_txt"].dropna().unique().tolist()) if "weaptype1_txt" in df.columns else []
selected_weapons = st.sidebar.multiselect("Weapon Categories", options=all_weapons, default=[])

# Casualty Threshold
min_casualties = st.sidebar.number_input("Minimum Fatalities (nkill)", min_value=0, max_value=5000, value=0)

# Freeform Search Input
st.sidebar.markdown("---")
st.sidebar.subheader("🔎 Text Query")
search_term = st.sidebar.text_input("Search (Group, City, Province, Narrative)", placeholder="e.g. Baghdad, Taliban, convoy...")

# ---------------------------------------------------------------------------
# Filter Application
# ---------------------------------------------------------------------------
filtered = df.copy()

# Year filtering
if "iyear" in filtered.columns:
    filtered = filtered[(filtered["iyear"] >= selected_years[0]) & (filtered["iyear"] <= selected_years[1])]

# Region filtering
if selected_regions and "region_txt" in filtered.columns:
    filtered = filtered[filtered["region_txt"].isin(selected_regions)]

# Country filtering
if selected_countries and "country_txt" in filtered.columns:
    filtered = filtered[filtered["country_txt"].isin(selected_countries)]

# Attack type filtering
if selected_attacks and "attacktype1_txt" in filtered.columns:
    filtered = filtered[filtered["attacktype1_txt"].isin(selected_attacks)]

# Target type filtering
if selected_targets and "targtype1_txt" in filtered.columns:
    filtered = filtered[filtered["targtype1_txt"].isin(selected_targets)]

# Weapon type filtering
if selected_weapons and "weaptype1_txt" in filtered.columns:
    filtered = filtered[filtered["weaptype1_txt"].isin(selected_weapons)]

# Casualty filtering
if min_casualties > 0 and "nkill" in filtered.columns:
    filtered = filtered[filtered["nkill"] >= min_casualties]

# Text search
if search_term.strip():
    term = search_term.strip().lower()
    search_cols = [c for c in ["gname", "city", "provstate", "summary", "country_txt"] if c in filtered.columns]
    match_mask = pd.Series(False, index=filtered.index)
    for c in search_cols:
        match_mask = match_mask | filtered[c].astype(str).str.lower().str.contains(term, na=False)
    filtered = filtered[match_mask]

# ---------------------------------------------------------------------------
# Telemetry Metrics
# ---------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Retrieved Records", f"{len(filtered):,}", delta=f"{len(filtered) - len(df):,} vs Total" if len(filtered) < len(df) else "100%")
col2.metric("Total Fatalities", f"{int(filtered['nkill'].sum()):,}" if 'nkill' in filtered.columns else "0")
col3.metric("Total Wounded", f"{int(filtered['nwound'].sum()):,}" if 'nwound' in filtered.columns else "0")
col4.metric("Active Theatres", f"{filtered['region_txt'].nunique() if 'region_txt' in filtered.columns else 0}")
col5.metric("Identified Factions", f"{filtered[filtered['gname'] != 'Unknown']['gname'].nunique() if 'gname' in filtered.columns else 0}")

st.markdown("---")

# ---------------------------------------------------------------------------
# Column Projection & Pagination
# ---------------------------------------------------------------------------
col_config, col_export = st.columns([3, 1])

with col_config:
    default_columns = [
        "iyear",
        "imonth",
        "iday",
        "country_txt",
        "region_txt",
        "city",
        "attacktype1_txt",
        "targtype1_txt",
        "weaptype1_txt",
        "gname",
        "nkill",
        "nwound",
        "summary",
    ]
    available_cols = [c for c in df.columns if c in default_columns] + [c for c in df.columns if c not in default_columns]
    selected_cols = st.multiselect(
        "Displayed Columns",
        options=available_cols,
        default=[c for c in default_columns if c in df.columns],
    )

with col_export:
    st.write("")
    st.write("")
    csv_bytes = filtered[selected_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Current Slice (CSV)",
        data=csv_bytes,
        file_name=f"gtd_slice_{selected_years[0]}_{selected_years[1]}.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ---------------------------------------------------------------------------
# Pagination Controls
# ---------------------------------------------------------------------------
total_rows = len(filtered)
if total_rows == 0:
    st.info("No records match the active filter criteria. Try expanding the temporal range or clearing search terms.")
else:
    page_col1, page_col2, page_col3 = st.columns([1, 1, 2])
    with page_col1:
        page_size = st.selectbox("Rows per page", options=[25, 50, 100, 250], index=1)

    total_pages = max(1, math.ceil(total_rows / page_size))

    with page_col2:
        current_page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    with page_col3:
        st.write("")
        st.caption(f"Showing page {current_page} of {total_pages} (records {(current_page - 1) * page_size + 1:,} to {min(current_page * page_size, total_rows):,} of {total_rows:,})")

    # Slice DataFrame for active page
    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_rows)
    page_df = filtered[selected_cols].iloc[start_idx:end_idx]

    # Display Paginated Table
    st.dataframe(
        page_df,
        use_container_width=True,
        height=520,
    )

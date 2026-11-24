"""
AI-Based Military Intelligence & Threat Analysis Dashboard
Main Entry Point & Intelligence Center Overview.
"""

import pandas as pd
import streamlit as st

from src.config import (
    ETHICAL_DISCLAIMER,
    MISSING_YEAR,
    PROCESSED_DATA_PATH,
)
from src.data_loader import load_dataset

st.set_page_config(
    page_title="AI Threat Intel Dashboard | GTD Analysis",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for military tactical styling
st.markdown(
    """
    <style>
    .main {
        background-color: #0E1117;
    }
    .metric-card {
        background: linear-gradient(135deg, #1A1D24 0%, #15181E 100%);
        border: 1px solid #2B313D;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .metric-label {
        color: #9E9E9E;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
    }
    .metric-value {
        color: #FAFAFA;
        font-size: 1.85rem;
        font-weight: 700;
        margin-top: 4px;
        font-family: 'Courier New', Courier, monospace;
    }
    .disclaimer-box {
        background-color: rgba(211, 47, 47, 0.12);
        border-left: 4px solid #D32F2F;
        padding: 14px 18px;
        border-radius: 4px;
        margin-bottom: 24px;
        font-size: 0.88rem;
        color: #E0E0E0;
    }
    .nav-card {
        background-color: #1A1D24;
        border: 1px solid #2B313D;
        border-radius: 8px;
        padding: 18px;
        height: 100%;
        transition: transform 0.2s;
    }
    .nav-card:hover {
        border-color: #D32F2F;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Loading Intelligence Dataset...")
def get_cached_gtd_data() -> pd.DataFrame:
    """Load cached cleaned GTD Parquet dataset."""
    return load_dataset(PROCESSED_DATA_PATH)


def main():
    # Sidebar Metadata
    st.sidebar.image("https://img.icons8.com/color/96/shield.png", width=64)
    st.sidebar.title("THREAT INTEL OPS")
    st.sidebar.caption("Global Terrorism Database (1970–2017)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### System Telemetry")

    # Load data
    try:
        df = get_cached_gtd_data()
        st.sidebar.success(f"● Parquet Active: {len(df):,} incidents")
        st.sidebar.info(f"Temporal Span: {df['iyear'].min()} – {df['iyear'].max()} (excl. {MISSING_YEAR})")
    except Exception as e:
        st.sidebar.error(f"Data loading failed: {e}")
        st.stop()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Ethical Classification")
    st.sidebar.caption(
        "Tier: Historical / Educational Academic Research.\n"
        "Strictly Non-Operational. No Tactical Targeting Capabilities."
    )

    # Header Section
    st.title("AI-Based Military Intelligence and Threat Analysis Dashboard")
    st.markdown(
        "#### *Tactical Pattern Recognition, Spatial Hotspotting & Predictive Risk Analytics on the Global Terrorism Database*"
    )

    # Mandated Ethical Disclaimer Box
    st.markdown(
        f"""
        <div class="disclaimer-box">
            <strong>⚠️ OPERATIONAL FRAMING & ETHICAL DIRECTIVE:</strong><br>
            {ETHICAL_DISCLAIMER}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # High-level System Architecture Cards
    col1, col2, col3, col4 = st.columns(4)

    total_incidents = len(df)
    total_fatalities = int(df["nkill"].sum())
    total_wounded = int(df["nwound"].sum())
    total_countries = df["country_txt"].nunique()

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Documented Incidents</div>
                <div class="metric-value">{total_incidents:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Recorded Fatalities</div>
                <div class="metric-value" style="color: #FF5252;">{total_fatalities:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Recorded Wounded</div>
                <div class="metric-value" style="color: #FFD600;">{total_wounded:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Impacted Sovereign States</div>
                <div class="metric-value" style="color: #00E5FF;">{total_countries:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation & Architecture Overview Grid
    st.markdown("### 🗂️ Intelligence Operations Directory")
    st.markdown("Select a module from the left sidebar navigation to begin analytical operations:")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            """
            <div class="nav-card">
                <h4>01 · Executive Summary</h4>
                <p style="color: #9E9E9E; font-size: 0.9rem;">
                    Macro intelligence overview, longitudinal incident-fatality trends, 1993 missing-archive annotation,
                    and theatre-level distributions.
                </p>
                <a href="/Home" target="_self">Launch 01_Home →</a>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            """
            <div class="nav-card">
                <h4>02 · Geospatial Threat Center</h4>
                <p style="color: #9E9E9E; font-size: 0.9rem;">
                    Global coordinates plotting, multi-decade animated temporal sliders, DBSCAN spatial density
                    clustering (hotspots), and tactical filters.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            """
            <div class="nav-card">
                <h4>04 · Predictive Tactic Classifier</h4>
                <p style="color: #9E9E9E; font-size: 0.9rem;">
                    Zero-leakage pre-attack classification with LightGBM/CatBoost, SHAP local waterfall & global
                    feature attribution.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    m4, m5, m6 = st.columns(3)
    with m4:
        st.markdown(
            """
            <div class="nav-card">
                <h4>06 · Strategic Composite Risk Index</h4>
                <p style="color: #9E9E9E; font-size: 0.9rem;">
                    Multi-factor country-year vulnerability index, Kendall-tau parameter sensitivity simulation,
                    and choropleth threat grading.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m5:
        st.markdown(
            """
            <div class="nav-card">
                <h4>09 · Early-Warning Surge Detection</h4>
                <p style="color: #9E9E9E; font-size: 0.9rem;">
                    Unsupervised anomaly detection (Isolation Forest + Rolling Z-Score) for regional escalation
                    and tactical surge flags.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m6:
        st.markdown(
            """
            <div class="nav-card">
                <h4>15 · Data Quality & Archival Audit</h4>
                <p style="color: #9E9E9E; font-size: 0.9rem;">
                    Decade missingness heatmaps, unknown perpetrator attribution drift, reporting bias methodology,
                    and annual intelligence quality score.
                </p>
                <a href="/Data_Quality" target="_self">Launch 15_Data_Quality →</a>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()

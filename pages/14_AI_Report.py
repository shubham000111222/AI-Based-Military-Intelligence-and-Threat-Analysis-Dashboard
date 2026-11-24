"""
Page 14: AI Threat Intelligence Report Generator
Synthesizes structured strategic threat briefs from aggregated data using Google Gemini
or deterministic templates, with downloadable executive PDF and CSV exports.
"""

import json

import streamlit as st

from src.config import (
    ETHICAL_DISCLAIMER,
)
from src.data_loader import load_dataset
from src.pdf_export import generate_pdf_report
from src.report import (
    build_threat_stats_summary,
    generate_deterministic_report,
    generate_gemini_report,
)

st.set_page_config(
    page_title="Strategic AI Report | AI Threat Intelligence",
    page_icon="📑",
    layout="wide",
)

st.title("📑 Strategic Threat Intelligence Report Generator")
st.caption(
    "Automated synthesis of executive intelligence briefs from historical GTD aggregates. "
    "Features privacy-preserving aggregate transmission, Gemini synthesis, and executive PDF export."
)

st.warning(f"⚖️ **Ethical & Analytical Framing**: {ETHICAL_DISCLAIMER}")


@st.cache_data
def get_data():
    return load_dataset()


df = get_data()

# ---------------------------------------------------------------------------
# Sidebar Scope Selection
# ---------------------------------------------------------------------------
st.sidebar.header("🎯 Briefing Scope")

min_yr = int(df["iyear"].min()) if "iyear" in df.columns else 1970
max_yr = int(df["iyear"].max()) if "iyear" in df.columns else 2017

selected_years = st.sidebar.slider(
    "Temporal Coverage",
    min_value=min_yr,
    max_value=max_yr,
    value=(min_yr, max_yr),
)

regions = ["All Regions"] + sorted(df["region_txt"].dropna().unique().tolist()) if "region_txt" in df.columns else ["All Regions"]
selected_region = st.sidebar.selectbox("Geographic Theatre", options=regions)

use_gemini = st.sidebar.checkbox("Enable Gemini Synthesis (if configured)", value=True)

# Build stats dict
stats = build_threat_stats_summary(
    df,
    region=selected_region if selected_region != "All Regions" else None,
    year_range=selected_years,
)

totals = stats["totals"]

# Aggregate KPI Header
st.subheader("Aggregated Threat Telemetry Preview")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Incidents", f"{totals['incidents']:,}")
kpi2.metric("Fatalities", f"{totals['fatalities']:,}")
kpi3.metric("Wounded", f"{totals['wounded']:,}")
kpi4.metric("Total Casualties", f"{totals['casualties']:,}")
kpi5.metric("Casualty Reporting Fidelity", f"{totals['casualty_reporting_rate_pct']:.1f}%")

st.markdown("---")

col_btn, col_info = st.columns([1, 2])
with col_btn:
    generate_pressed = st.button("🚀 Generate Executive Intelligence Brief", type="primary", use_container_width=True)

with col_info:
    st.info(
        "🔒 **Zero Raw Data Transmission**: Analysis engine transmits strictly aggregated statistical counts "
        "(totals, top factions, tactics) to the LLM. Raw incident rows and personally identifiable records are never sent."
    )

if generate_pressed or "current_report" in st.session_state:
    if generate_pressed:
        with st.spinner("Synthesizing strategic threat brief..."):
            if use_gemini:
                report_markdown = generate_gemini_report(stats)
            else:
                report_markdown = generate_deterministic_report(stats)
            st.session_state["current_report"] = report_markdown
            st.session_state["current_stats"] = stats
    else:
        report_markdown = st.session_state["current_report"]
        stats = st.session_state.get("current_stats", stats)

    st.markdown("---")

    # Export Actions Header
    st.subheader("Executive Document Actions")
    exp_c1, exp_c2, _ = st.columns([1, 1, 2])

    with exp_c1:
        pdf_bytes = generate_pdf_report(report_markdown, stats)
        filename_region = selected_region.replace(" ", "_").replace("&", "and")
        st.download_button(
            label="📥 Download Executive Brief (PDF)",
            data=pdf_bytes,
            file_name=f"threat_brief_{filename_region}_{selected_years[0]}_{selected_years[1]}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with exp_c2:
        stats_json = json.dumps(stats, indent=2)
        st.download_button(
            label="📊 Export Aggregates (JSON)",
            data=stats_json,
            file_name=f"threat_stats_{filename_region}_{selected_years[0]}_{selected_years[1]}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown(report_markdown)

else:
    st.markdown("### Ready to Generate Briefing")
    st.write(
        "Click the **Generate Executive Intelligence Brief** button above to compile a comprehensive, "
        "multi-section retrospective strategic briefing for the chosen theatre and time window."
    )

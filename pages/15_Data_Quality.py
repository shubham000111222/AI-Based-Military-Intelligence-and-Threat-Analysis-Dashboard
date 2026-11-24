"""
15_Data_Quality.py - Archival Integrity, Missingness & Reporting Bias Auditing.
Evaluates GTD collection fidelity across decades:
- Missingness heatmaps per column and per decade
- Unknown perpetrator attribution drift
- Casualty reporting completeness
- Geocoding and coordinate precision audit
- The 1993 archival loss explanation
- Methodological reporting bias explainer
- Annual Data Quality Index (0–100)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import (
    ETHICAL_DISCLAIMER,
    PROCESSED_DATA_PATH,
)
from src.data_loader import load_dataset
from src.data_quality import (
    compute_annual_data_quality_scores,
    compute_casualty_reporting_rate_by_year,
    compute_coordinate_precision_stats,
    compute_missingness_by_decade,
    compute_unknown_perpetrators_by_year,
    get_1993_gap_info,
    get_reporting_bias_context,
)

st.set_page_config(
    page_title="Data Quality & Integrity Audit | GTD Analysis",
    page_icon="🔍",
    layout="wide",
)


@st.cache_data(show_spinner="Auditing Intelligence Dataset...")
def get_audit_data() -> pd.DataFrame:
    return load_dataset(PROCESSED_DATA_PATH)


def main():
    st.title("15 · Data Quality, Archival Integrity & Reporting Bias")
    st.caption("Methodological Health Audit and Longitudinal Documentation Integrity (1970–2017)")

    st.info(f"**RESEARCH INTEGRITY DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    df = get_audit_data()

    # Section 1: Executive Integrity KPIs
    st.markdown("### 🔍 Archival Integrity Indicators")
    coord_stats = compute_coordinate_precision_stats(df)
    unknown_df = compute_unknown_perpetrators_by_year(df)
    overall_unknown_pct = round(
        float((df["gname"] == "Unknown").sum() / len(df) * 100), 1
    )
    cas_df = compute_casualty_reporting_rate_by_year(df)
    overall_cas_known_pct = round(
        float(df["casualties_known"].mean() * 100), 1
    ) if "casualties_known" in df.columns else 90.0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            label="CASUALTY COMPLETENESS",
            value=f"{overall_cas_known_pct}%",
            help="Share of incidents with verified casualty numbers (killed or wounded).",
        )
    with k2:
        st.metric(
            label="GEOCODING PINPOINT RATE",
            value=f"{coord_stats['pinpoint_coords_pct']}%",
            help="High-precision coordinates (excluding missing and integer centroids).",
        )
    with k3:
        st.metric(
            label="UNCLAIMED ATTRIBUTION RATE",
            value=f"{overall_unknown_pct}%",
            help="Incidents where the perpetrator group remains classified as 'Unknown'.",
        )
    with k4:
        st.metric(
            label="MISSING COORD RATE",
            value=f"{coord_stats['missing_coords_pct']}%",
            help="Incidents lacking valid geospatial coordinates.",
        )

    st.markdown("---")

    # Section 2: Annual Composite Data Quality Index (0 - 100)
    st.markdown("### 🏆 Annual Data Quality Index (0 – 100)")
    st.markdown(
        "A composite benchmark scoring intelligence completeness on four equal 25-point pillars: "
        "**(1)** Casualty documentation completeness, **(2)** Geocoding precision and boundary validity, "
        "**(3)** Perpetrator organizational attribution, and **(4)** Descriptive narrative coverage."
    )

    quality_df = compute_annual_data_quality_scores(df)

    fig_dq = go.Figure()

    fig_dq.add_trace(
        go.Scatter(
            x=quality_df["iyear"],
            y=quality_df["data_quality_score"],
            mode="lines+markers",
            name="Overall Quality Score",
            line=dict(color="#00E5FF", width=3),
            marker=dict(size=6, color="#00E5FF"),
        )
    )

    # Sub-pillar lines
    fig_dq.add_trace(
        go.Scatter(
            x=quality_df["iyear"],
            y=quality_df["casualty_completeness_pct"],
            mode="lines",
            name="Casualty Reporting %",
            line=dict(color="#00E676", width=1.5, dash="dot"),
        )
    )
    fig_dq.add_trace(
        go.Scatter(
            x=quality_df["iyear"],
            y=quality_df["group_attribution_pct"],
            mode="lines",
            name="Identified Group %",
            line=dict(color="#FFD600", width=1.5, dash="dot"),
        )
    )
    fig_dq.add_trace(
        go.Scatter(
            x=quality_df["iyear"],
            y=quality_df["narrative_coverage_pct"],
            mode="lines",
            name="Summary Text %",
            line=dict(color="#FF1744", width=1.5, dash="dot"),
        )
    )

    # Annotate 1993 gap
    fig_dq.add_vrect(
        x0=1992.5,
        x1=1993.5,
        fillcolor="#FF9100",
        opacity=0.3,
        line_width=1.5,
        line_color="#FF9100",
        line_dash="dash",
        annotation_text="1993 Missing Archive",
        annotation_position="top left",
        annotation=dict(font_size=11, font_color="#FF9100"),
    )

    fig_dq.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#1A1D24",
        xaxis=dict(title="Observation Year", dtick=5, gridcolor="#2B313D"),
        yaxis=dict(title="Quality Index / Percentage", range=[0, 105], gridcolor="#2B313D"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=30, b=40),
        height=420,
    )
    st.plotly_chart(fig_dq, use_container_width=True)

    st.markdown("---")

    # Section 3: Missingness Heatmap per Column & Decade
    st.markdown("### 🧩 Missingness Across Attributes & Decades")
    st.caption("Percentage of records missing or empty for core analytical columns across each operational decade.")

    decade_matrix = compute_missingness_by_decade(df)

    fig_heat = px.imshow(
        decade_matrix,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="Reds",
        labels=dict(x="Decade", y="Analytical Attribute", color="Missing %"),
        template="plotly_dark",
    )
    fig_heat.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#1A1D24",
        margin=dict(l=40, r=40, t=30, b=40),
        height=380,
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")

    # Section 4: Deep Dive - Unknown Perpetrators & Casualty Reporting
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown("#### Unclaimed / 'Unknown' Perpetrator Rate")
        st.caption("Share of attacks without documented organizational attribution.")

        fig_unk = go.Figure()
        fig_unk.add_trace(
            go.Scatter(
                x=unknown_df["iyear"],
                y=unknown_df["unknown_pct"],
                mode="lines+markers",
                line=dict(color="#FF5252", width=2.5),
                marker=dict(size=4),
                name="% Unclaimed",
                fill="tozeroy",
                fillcolor="rgba(255, 82, 82, 0.15)",
            )
        )
        fig_unk.add_vrect(
            x0=1992.5,
            x1=1993.5,
            fillcolor="#FF9100",
            opacity=0.25,
            line_width=1,
            line_dash="dot",
        )
        fig_unk.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#1A1D24",
            xaxis=dict(title="Year", dtick=5, gridcolor="#2B313D"),
            yaxis=dict(title="% Unknown Perpetrators", range=[0, 100], gridcolor="#2B313D"),
            margin=dict(l=20, r=20, t=20, b=20),
            height=320,
        )
        st.plotly_chart(fig_unk, use_container_width=True)

    with c_right:
        st.markdown("#### Casualty Verification Completeness")
        st.caption("Annual percentage of incidents with known casualty figures.")

        fig_cas = go.Figure()
        fig_cas.add_trace(
            go.Scatter(
                x=cas_df["iyear"],
                y=cas_df["known_rate_pct"],
                mode="lines+markers",
                line=dict(color="#00E676", width=2.5),
                marker=dict(size=4),
                name="% Known Casualties",
                fill="tozeroy",
                fillcolor="rgba(0, 230, 118, 0.12)",
            )
        )
        fig_cas.add_vrect(
            x0=1992.5,
            x1=1993.5,
            fillcolor="#FF9100",
            opacity=0.25,
            line_width=1,
            line_dash="dot",
        )
        fig_cas.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#1A1D24",
            xaxis=dict(title="Year", dtick=5, gridcolor="#2B313D"),
            yaxis=dict(title="% Known Casualties", range=[0, 105], gridcolor="#2B313D"),
            margin=dict(l=20, r=20, t=20, b=20),
            height=320,
        )
        st.plotly_chart(fig_cas, use_container_width=True)

    st.markdown("---")

    # Section 5: Coordinate Precision Audit Breakdown
    st.markdown("### 📍 Geocoding Fidelity & Coordinate Resolution")
    col_p1, col_p2 = st.columns([1, 2])

    with col_p1:
        coord_donut_df = pd.DataFrame([
            {"Type": "Pinpoint Coordinates", "Count": coord_stats["pinpoint_coords_count"]},
            {"Type": "Approximate Centroids", "Count": coord_stats["approx_centroids_count"]},
            {"Type": "Missing Coordinates", "Count": coord_stats["missing_coords_count"]},
        ])
        fig_donut = px.pie(
            coord_donut_df,
            values="Count",
            names="Type",
            hole=0.5,
            template="plotly_dark",
            color="Type",
            color_discrete_map={
                "Pinpoint Coordinates": "#00E676",
                "Approximate Centroids": "#FFD600",
                "Missing Coordinates": "#FF1744",
            },
        )
        fig_donut.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#1A1D24",
            margin=dict(l=10, r=10, t=20, b=20),
            height=300,
            showlegend=False,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_p2:
        st.markdown(
            f"""
            - **Pinpoint Tactical Coordinates ({coord_stats['pinpoint_coords_pct']}%):** High-precision latitude/longitude
              suitable for density hotspotting and exact spatial clustering.
            - **Approximate Centroids ({coord_stats['approx_centroids_pct']}%):** Integer-rounded coordinates typically
              reflecting capital city or provincial administrative centroids rather than exact ambush coordinates.
            - **Missing Coordinates ({coord_stats['missing_coords_pct']}%):** Incidents with unknown geospatial coordinates.
              *Critical rule: Retained for tabular and machine learning models, filtered out solely for geographic maps.*
            """
        )

    st.markdown("---")

    # Section 6: Historical Gap & Reporting Bias Context
    gap_info = get_1993_gap_info()
    st.markdown(f"### 🗄️ {gap_info['title']}")
    st.markdown(
        f"""
        > **Status:** {gap_info['status']}
        > **Archival Root Cause:** {gap_info['cause']}
        > **Analytical Impact:** {gap_info['impact']}
        > **Operational Protocol:** {gap_info['methodological_recommendation']}
        """
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📰 Reporting Bias & Methodological Regimes")
    st.markdown(
        "Terrorism event datasets do not measure violence directly; they measure the *documentation of political violence* "
        "filtered through media institutions, intelligence collection mandates, and communication infrastructure."
    )

    bias_items = get_reporting_bias_context()
    for item in bias_items:
        with st.expander(f"📌 {item['dimension']} — Impact: {item['impact']}", expanded=True):
            st.write(item["mechanism"])


if __name__ == "__main__":
    main()

"""
06_Risk_Index.py - Strategic Composite Country Risk Index.
Features:
- Multi-criteria sovereign threat ranking (incidents, casualties, 3-yr momentum, mass casualty ratio)
- Global Choropleth threat map
- Country drill-down with radar component breakdown and historical trajectory
- Documented methodology explainer and quantile tier thresholds.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import (
    DEFAULT_RISK_WEIGHTS,
    ETHICAL_DISCLAIMER,
    MISSING_YEAR,
    PROCESSED_DATA_PATH,
)
from src.data_loader import load_dataset
from src.risk_index import calculate_risk_index

st.set_page_config(
    page_title="Strategic Risk Index | GTD Analysis",
    page_icon="🛡️",
    layout="wide",
)


@st.cache_data(show_spinner="Loading Intelligence Dataset...")
def get_risk_data():
    return load_dataset(PROCESSED_DATA_PATH)


def main():
    st.title("06 · Strategic Composite Country Risk Index")
    st.caption("Multi-Factor Sovereign Vulnerability Benchmark & Quantile Threat Classification")

    st.info(f"**HISTORICAL & RESEARCH DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    df = get_risk_data()

    # Year Selector
    available_years = sorted([y for y in df["iyear"].unique() if y != MISSING_YEAR])
    default_year = max(available_years)

    st.sidebar.markdown("### 🎛️ Assessment Period")
    eval_year = st.sidebar.select_slider(
        "Evaluation Year",
        options=available_years,
        value=default_year,
    )

    # Compute risk index
    risk_df = calculate_risk_index(df, year=eval_year)

    if risk_df.empty:
        st.warning(f"No incident data available to compute risk index for {eval_year}.")
        st.stop()

    # Executive Overview
    st.markdown(f"### 🌐 Global Risk Distribution ({eval_year})")
    k1, k2, k3, k4 = st.columns(4)

    tier_counts = risk_df["risk_tier"].value_counts()
    with k1:
        st.metric("CRITICAL TIER STATES", f"{tier_counts.get('Critical', 0)} countries", delta_color="inverse")
    with k2:
        st.metric("HIGH TIER STATES", f"{tier_counts.get('High', 0)} countries")
    with k3:
        st.metric("MEDIUM TIER STATES", f"{tier_counts.get('Medium', 0)} countries")
    with k4:
        st.metric("LOW TIER STATES", f"{tier_counts.get('Low', 0)} countries")

    # Global Choropleth
    fig_choro = px.choropleth(
        risk_df,
        locations="country_txt",
        locationmode="country names",
        color="risk_score",
        hover_name="country_txt",
        hover_data={
            "risk_score": True,
            "risk_tier": True,
            "incidents": True,
            "casualties": True,
            "country_txt": False,
        },
        color_continuous_scale="Reds",
        range_color=[0, 100],
        template="plotly_dark",
        title=f"Composite Sovereign Threat Heatmap ({eval_year})",
    )
    fig_choro.update_geos(
        bgcolor="#0E1117",
        showcountries=True,
        countrycolor="#2B313D",
        showcoastlines=True,
        coastlinecolor="#37474F",
        showland=True,
        landcolor="#1A1D24",
        showocean=True,
        oceancolor="#0E1117",
    )
    fig_choro.update_layout(
        paper_bgcolor="#0E1117",
        margin=dict(l=0, r=0, t=40, b=0),
        height=500,
    )
    st.plotly_chart(fig_choro, use_container_width=True)

    st.markdown("---")

    # Section 2: Ranked Country Table
    st.markdown("### 📋 Sovereign Threat Ranking")
    st.caption("Ordered by Composite Strategic Risk Score (0 to 100):")

    display_df = risk_df[[
        "rank",
        "country_txt",
        "region_txt",
        "risk_tier",
        "risk_score",
        "incidents",
        "casualties",
        "trend_slope",
        "mass_casualty_ratio",
    ]].rename(columns={
        "rank": "Rank",
        "country_txt": "Sovereign State",
        "region_txt": "Theatre",
        "risk_tier": "Risk Tier",
        "risk_score": "Risk Score",
        "incidents": "Incidents",
        "casualties": "Casualties",
        "trend_slope": "3-Yr Momentum",
        "mass_casualty_ratio": "Mass Casualty %",
    })

    # Color code tiers
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # Section 3: Country Drill-Down & Component Decomposition
    st.markdown("### 🔎 Sovereign State Component Drill-Down")
    selected_country = st.selectbox("Select State for Tactical Component Audit", risk_df["country_txt"].tolist(), index=0)

    country_row = risk_df[risk_df["country_txt"] == selected_country].iloc[0]

    c_radar, c_hist = st.columns([1, 1])

    with c_radar:
        st.markdown(f"#### Component Decomposition: **{selected_country}**")
        st.markdown(f"**Composite Score:** `{country_row['risk_score']}` | **Tier:** `{country_row['risk_tier']}`")

        categories = [
            "Incident Volume",
            "Casualty Severity",
            "3-Yr Momentum",
            "Mass-Casualty Vulnerability",
        ]
        values = [
            country_row["norm_incidents"],
            country_row["norm_casualties"],
            country_row["norm_trend"],
            country_row["norm_mass_casualty"],
        ]

        fig_radar = go.Figure()
        fig_radar.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name=selected_country,
                line=dict(color="#FF1744", width=2),
                fillcolor="rgba(255, 23, 68, 0.25)",
            )
        )
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2B313D"),
                bgcolor="#1A1D24",
            ),
            paper_bgcolor="#0E1117",
            showlegend=False,
            margin=dict(l=30, r=30, t=20, b=20),
            height=320,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with c_hist:
        st.markdown("#### Longitudinal Risk Trajectory")
        st.caption("Multi-year composite risk index evolution for selected state:")

        # Compute multi-year trajectory for selected country
        country_hist_records = []
        recent_years = [y for y in available_years if y >= max(available_years) - 10]
        for yr in recent_years:
            yr_df = calculate_risk_index(df, year=yr)
            sub_c = yr_df[yr_df["country_txt"] == selected_country]
            if not sub_c.empty:
                country_hist_records.append({
                    "Year": yr,
                    "Score": sub_c.iloc[0]["risk_score"],
                    "Tier": sub_c.iloc[0]["risk_tier"],
                })

        if country_hist_records:
            hist_df = pd.DataFrame(country_hist_records)
            fig_hist = px.line(
                hist_df,
                x="Year",
                y="Score",
                markers=True,
                template="plotly_dark",
            )
            fig_hist.update_traces(line_color="#00E5FF", line_width=2.5, marker=dict(size=6))
            fig_hist.update_layout(
                paper_bgcolor="#0E1117",
                plot_bgcolor="#1A1D24",
                yaxis=dict(range=[0, 105], gridcolor="#2B313D"),
                xaxis=dict(dtick=1, gridcolor="#2B313D"),
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Insufficient longitudinal data for historical risk trajectory.")

    st.markdown("---")

    # Section 4: Methodology Explainer
    with st.expander("📖 Strategic Risk Index Methodology & Formulation", expanded=False):
        st.markdown(
            f"""
            #### Index Formulation
            The **Composite Country Risk Index** integrates four normalized operational pillars:
            $$\\text{{Risk Score}} = w_1 \\cdot \\widetilde{{\\log(1 + N_i)}} + w_2 \\cdot \\widetilde{{\\log(1 + C_i)}} + w_3 \\cdot \\widetilde{{\\beta_i}} + w_4 \\cdot \\widetilde{{M_i}}$$

            1. **Incident Volume ($N_i$):** Natural logarithm of annual incidents, min-max normalized across sovereign states ($w_1 = {DEFAULT_RISK_WEIGHTS['log_incidents']}$).
            2. **Casualty Severity ($C_i$):** Natural logarithm of cumulative fatalities and wounded ($w_2 = {DEFAULT_RISK_WEIGHTS['log_casualties']}$). Logarithmic scaling prevents mega-outliers from compressing variance.
            3. **3-Year Momentum Slope ($\\beta_i$):** Linear regression slope across trailing 3 years $(t-2, t-1, t)$ measuring acceleration ($w_3 = {DEFAULT_RISK_WEIGHTS['trend_slope']}$).
            4. **Mass-Casualty Vulnerability ($M_i$):** Proportion of attacks with $\\ge 10$ casualties ($w_4 = {DEFAULT_RISK_WEIGHTS['mass_casualty_ratio']}$).

            #### Risk Tier Quantile Cutoffs
            - **Low Risk:** 0th – 40th percentile of annual scores.
            - **Medium Risk:** 40th – 70th percentile.
            - **High Risk:** 70th – 90th percentile.
            - **Critical Threat:** Top 10th percentile (90th – 100th percentile).
            """
        )


if __name__ == "__main__":
    main()

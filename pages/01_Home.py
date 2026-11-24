"""
01_Home.py - Executive Strategic Intelligence Overview.
Presents KPI summaries, longitudinal trends with the 1993 archival gap explicitly annotated,
regional distribution, and leading perpetrator groups.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.anomaly import get_top_recent_alerts
from src.config import (
    ARTIFACTS_DIR,
    ETHICAL_DISCLAIMER,
    MISSING_YEAR,
    MISSING_YEAR_ANNOTATION,
    PROCESSED_DATA_PATH,
    UNKNOWN_GROUP_NAME,
)
from src.data_loader import load_dataset

st.set_page_config(
    page_title="Executive Intel Overview | GTD Analysis",
    page_icon="🛡️",
    layout="wide",
)


@st.cache_data(show_spinner="Loading Intelligence Dataset...")
def get_data() -> pd.DataFrame:
    return load_dataset(PROCESSED_DATA_PATH)


def main():
    st.title("01 · Executive Threat Overview & Strategic Trends")
    st.caption("Historical Intelligence Analysis across Global Incidents (1970–2017)")

    # Mandatory Ethical Disclaimer
    st.info(f"**HISTORICAL & RESEARCH DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    df = get_data()

    # Sidebar Filter Controls
    st.sidebar.markdown("### 🎛️ Strategic Filters")
    min_year = int(df["iyear"].min())
    max_year = int(df["iyear"].max())

    selected_years = st.sidebar.slider(
        "Observation Window",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
    )

    all_regions = ["All Regions"] + sorted(df["region_txt"].dropna().unique().tolist())
    selected_region = st.sidebar.selectbox("Geographic Theatre", all_regions)

    # Filter DataFrame
    filtered_df = df[
        (df["iyear"] >= selected_years[0])
        & (df["iyear"] <= selected_years[1])
    ]
    if selected_region != "All Regions":
        filtered_df = filtered_df[filtered_df["region_txt"] == selected_region]

    # KPI Summary Cards
    st.markdown("### 📊 Macro Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)

    tot_incidents = len(filtered_df)
    tot_fatalities = int(filtered_df["nkill"].sum())
    tot_wounded = int(filtered_df["nwound"].sum())
    tot_countries = filtered_df["country_txt"].nunique()
    span_years = f"{selected_years[0]} – {selected_years[1]}"

    with col1:
        st.metric(label="TOTAL INCIDENTS", value=f"{tot_incidents:,}")
    with col2:
        st.metric(label="TOTAL FATALITIES", value=f"{tot_fatalities:,}")
    with col3:
        st.metric(label="TOTAL WOUNDED", value=f"{tot_wounded:,}")
    with col4:
        st.metric(label="SOVEREIGN STATES", value=f"{tot_countries:,}")
    with col5:
        st.metric(label="YEAR SPAN", value=span_years)

    st.markdown("---")

    # Longitudinal Trend Chart with 1993 Data Gap Annotation
    st.markdown("### 📈 Longitudinal Threat Trajectory & Casualty Volume")
    st.caption(
        "Annual incident frequency and cumulative fatalities. "
        "Notice the explicit discontinuity at 1993 representing missing archival records."
    )

    # Aggregate by year
    annual_agg = (
        filtered_df.groupby("iyear")
        .agg(
            incidents=("iyear", "count"),
            fatalities=("nkill", "sum"),
            wounded=("nwound", "sum"),
        )
        .reset_index()
    )

    fig_trend = go.Figure()

    # Bar chart for incidents
    fig_trend.add_trace(
        go.Bar(
            x=annual_agg["iyear"],
            y=annual_agg["incidents"],
            name="Incidents",
            marker_color="#37474F",
            opacity=0.75,
            yaxis="y1",
        )
    )

    # Line chart for fatalities
    fig_trend.add_trace(
        go.Scatter(
            x=annual_agg["iyear"],
            y=annual_agg["fatalities"],
            name="Fatalities",
            mode="lines+markers",
            line=dict(color="#FF1744", width=2.5),
            marker=dict(size=5),
            yaxis="y2",
        )
    )

    # Check if 1993 falls within selected window to add prominent annotation
    if selected_years[0] <= MISSING_YEAR <= selected_years[1]:
        # Add shaded rect or vertical marker
        fig_trend.add_vrect(
            x0=1992.5,
            x1=1993.5,
            fillcolor="#FF9100",
            opacity=0.25,
            line_width=1.5,
            line_color="#FF9100",
            line_dash="dash",
            annotation_text="1993 Data Gap",
            annotation_position="top left",
            annotation=dict(font_size=11, font_color="#FF9100"),
        )

    fig_trend.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#1A1D24",
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(
            title="Observation Year",
            dtick=5,
            showgrid=True,
            gridcolor="#2B313D",
        ),
        yaxis=dict(
            title="Annual Incidents",
            showgrid=True,
            gridcolor="#2B313D",
        ),
        yaxis2=dict(
            title="Annual Fatalities",
            overlaying="y",
            side="right",
            showgrid=False,
            color="#FF1744",
        ),
        hovermode="x unified",
        height=450,
    )

    st.plotly_chart(fig_trend, use_container_width=True)

    if selected_years[0] <= MISSING_YEAR <= selected_years[1]:
        st.warning(f"⚠️ **Archival Gap Notice (1993)**: {MISSING_YEAR_ANNOTATION}")

    st.markdown("---")

    # Breakdowns: Top Regions & Perpetrator Groups
    st.markdown("### 🌍 Spatial Theatres & Perpetrator Attribution")
    col_reg, col_grp = st.columns([1, 1])

    with col_reg:
        st.markdown("#### Incidents by Geographic Theatre")
        reg_counts = (
            filtered_df["region_txt"]
            .value_counts()
            .reset_index()
        )
        reg_counts.columns = ["Region", "Incidents"]
        fig_reg = px.bar(
            reg_counts.head(10),
            x="Incidents",
            y="Region",
            orientation="h",
            color="Incidents",
            color_continuous_scale="Reds",
            template="plotly_dark",
        )
        fig_reg.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#1A1D24",
            margin=dict(l=20, r=20, t=30, b=20),
            yaxis=dict(autorange="reversed"),
            height=380,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_grp:
        st.markdown("#### Leading Perpetrator Groups")
        include_unknown = st.checkbox("Include 'Unknown / Unclaimed' Perpetrators", value=False)
        grp_df = filtered_df if include_unknown else filtered_df[filtered_df["gname"] != UNKNOWN_GROUP_NAME]

        grp_counts = (
            grp_df["gname"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        grp_counts.columns = ["Perpetrator Group", "Incidents"]

        fig_grp = px.bar(
            grp_counts,
            x="Incidents",
            y="Perpetrator Group",
            orientation="h",
            color="Incidents",
            color_continuous_scale="Viridis",
            template="plotly_dark",
        )
        fig_grp.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#1A1D24",
            margin=dict(l=20, r=20, t=30, b=20),
            yaxis=dict(autorange="reversed"),
            height=380,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_grp, use_container_width=True)

    st.markdown("---")

    # Secondary Breakdown: Tactics & Weaponry
    st.markdown("### 🎯 Operational Tactics & Weaponry Breakdown")
    col_targ, col_weap = st.columns(2)

    with col_targ:
        st.markdown("#### Dominant Target Categories")
        targ_counts = (
            filtered_df["targtype1_txt"]
            .value_counts()
            .head(8)
            .reset_index()
        )
        targ_counts.columns = ["Target Type", "Count"]
        fig_targ = px.pie(
            targ_counts,
            values="Count",
            names="Target Type",
            hole=0.45,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Darkmint,
        )
        fig_targ.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#1A1D24",
            margin=dict(l=10, r=10, t=20, b=20),
            height=320,
        )
        st.plotly_chart(fig_targ, use_container_width=True)

    with col_weap:
        st.markdown("#### Primary Weapon Profiles")
        weap_counts = (
            filtered_df["weaptype1_txt"]
            .value_counts()
            .head(8)
            .reset_index()
        )
        weap_counts.columns = ["Weapon Type", "Count"]
        fig_weap = px.pie(
            weap_counts,
            values="Count",
            names="Weapon Type",
            hole=0.45,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Burg,
        )
        fig_weap.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#1A1D24",
            margin=dict(l=10, r=10, t=20, b=20),
            height=320,
        )
        st.plotly_chart(fig_weap, use_container_width=True)

    st.markdown("---")

    # Top 5 Historical Tactical Surge Alerts Section
    st.markdown("### 🚨 Top Historical Tactical Surge Alerts")
    st.caption("Highest-severity statistical anomalies identified by early-warning detection engines:")

    alerts_parquet = ARTIFACTS_DIR / "anomaly_alerts.parquet"
    if alerts_parquet.exists():
        panel_alerts = pd.read_parquet(alerts_parquet)
        top_5_alerts = get_top_recent_alerts(panel_alerts, top_n=5)
        st.dataframe(top_5_alerts, use_container_width=True, hide_index=True)
    else:
        st.info("Run 'python scripts/evaluate_anomaly.py' to generate precomputed early warning alerts.")


if __name__ == "__main__":
    main()

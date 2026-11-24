"""
03_Country_Analysis.py - Sovereign State Threat Deep Dive & Regional Benchmarking.
Features:
- Sovereign country selector with longitudinal incident & casualty trends (1993 gap annotated)
- Comparison against the regional average (annual incident benchmark)
- Tactic, weapon, and target breakdowns
- Deadliest documented incidents dossier
- Primary active perpetrator factions in the national theatre.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import (
    ETHICAL_DISCLAIMER,
    MISSING_YEAR,
    PROCESSED_DATA_PATH,
    UNKNOWN_GROUP_NAME,
)
from src.data_loader import load_dataset

st.set_page_config(
    page_title="Country Threat Analysis | GTD Analysis",
    page_icon="🔎",
    layout="wide",
)


@st.cache_data(show_spinner="Loading Intelligence Dataset...")
def get_country_data() -> pd.DataFrame:
    return load_dataset(PROCESSED_DATA_PATH)


def main():
    st.title("03 · Sovereign State Deep Dive & Regional Benchmark")
    st.caption("National Threat Profile, Tactical Signatures, and Deadliest Incidents (1970–2017)")

    st.info(f"**HISTORICAL & RESEARCH DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    df = get_country_data()

    # Country Selector in Sidebar
    all_countries = sorted(df["country_txt"].dropna().unique().tolist())

    # Pre-select high-volume country if available
    default_country = "Iraq" if "Iraq" in all_countries else all_countries[0]
    selected_country = st.sidebar.selectbox("Select Sovereign State", all_countries, index=all_countries.index(default_country))

    # Year slider
    min_yr = int(df["iyear"].min())
    max_yr = int(df["iyear"].max())
    selected_years = st.sidebar.slider(
        "Observation Span",
        min_value=min_yr,
        max_value=max_yr,
        value=(min_yr, max_yr),
        step=1,
    )

    # Subsets
    df_window = df[(df["iyear"] >= selected_years[0]) & (df["iyear"] <= selected_years[1])]
    country_df = df_window[df_window["country_txt"] == selected_country]

    if len(country_df) == 0:
        st.warning(f"No recorded incidents for '{selected_country}' within {selected_years[0]}–{selected_years[1]}.")
        st.stop()

    # Region determination
    theatre_region = country_df["region_txt"].iloc[0] if not country_df.empty else "Unknown"

    # Executive Country KPIs
    st.markdown(f"### 🚩 National Profile: **{selected_country}** ({theatre_region})")

    k1, k2, k3, k4, k5 = st.columns(5)
    c_incidents = len(country_df)
    c_kills = int(country_df["nkill"].sum())
    c_wounds = int(country_df["nwound"].sum())
    c_lethality = round(c_kills / c_incidents, 2) if c_incidents > 0 else 0.0

    # Regional comparison metrics
    region_df = df_window[df_window["region_txt"] == theatre_region]
    region_total_incidents = len(region_df)
    country_regional_share = round((c_incidents / region_total_incidents * 100), 1) if region_total_incidents > 0 else 0.0

    with k1:
        st.metric("NATIONAL INCIDENTS", f"{c_incidents:,}")
    with k2:
        st.metric("RECORDED FATALITIES", f"{c_kills:,}")
    with k3:
        st.metric("RECORDED WOUNDED", f"{c_wounds:,}")
    with k4:
        st.metric("LETHALITY RATE", f"{c_lethality} k/inc")
    with k5:
        st.metric("REGIONAL VIOLENCE SHARE", f"{country_regional_share}%")

    st.markdown("---")

    # Section 1: Longitudinal Trend (with 1993 gap annotated)
    st.markdown("### 📈 Longitudinal Threat Trajectory (with 1993 Archival Gap)")
    annual_country = (
        country_df.groupby("iyear")
        .agg(
            incidents=("iyear", "count"),
            fatalities=("nkill", "sum"),
            wounded=("nwound", "sum"),
        )
        .reset_index()
    )

    fig_ctrend = go.Figure()
    fig_ctrend.add_trace(
        go.Bar(
            x=annual_country["iyear"],
            y=annual_country["incidents"],
            name="National Incidents",
            marker_color="#455A64",
            opacity=0.8,
            yaxis="y1",
        )
    )
    fig_ctrend.add_trace(
        go.Scatter(
            x=annual_country["iyear"],
            y=annual_country["fatalities"],
            name="Fatalities",
            mode="lines+markers",
            line=dict(color="#FF1744", width=2.5),
            marker=dict(size=5),
            yaxis="y2",
        )
    )

    if selected_years[0] <= MISSING_YEAR <= selected_years[1]:
        fig_ctrend.add_vrect(
            x0=1992.5,
            x1=1993.5,
            fillcolor="#FF9100",
            opacity=0.3,
            line_width=1.5,
            line_dash="dash",
            annotation_text="1993 Data Gap",
            annotation_position="top left",
            annotation=dict(font_size=11, font_color="#FF9100"),
        )

    fig_ctrend.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#1A1D24",
        xaxis=dict(title="Observation Year", dtick=5, gridcolor="#2B313D"),
        yaxis=dict(title="Annual Incidents", gridcolor="#2B313D"),
        yaxis2=dict(
            title="Annual Fatalities",
            overlaying="y",
            side="right",
            showgrid=False,
            color="#FF1744",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=30, b=40),
        height=400,
    )
    st.plotly_chart(fig_ctrend, use_container_width=True)

    st.markdown("---")

    # Section 2: Comparison against Regional Average
    st.markdown(f"### ⚖️ National Incidents vs. Regional Peer Average ({theatre_region})")
    st.caption(
        f"Compares annual incident volume in {selected_country} against the mean annual incident "
        f"volume across all other states within {theatre_region}."
    )

    # Compute other countries in region
    other_region_df = region_df[region_df["country_txt"] != selected_country]
    num_other_countries = other_region_df["country_txt"].nunique()

    if num_other_countries > 0:
        regional_annual = (
            other_region_df.groupby("iyear")["country_txt"]
            .count()
            .reset_index(name="total_other_incidents")
        )
        regional_annual["regional_mean_incidents"] = (
            regional_annual["total_other_incidents"] / num_other_countries
        ).round(1)

        # Merge with country
        merged_benchmark = pd.merge(
            annual_country[["iyear", "incidents"]].rename(columns={"incidents": "country_incidents"}),
            regional_annual[["iyear", "regional_mean_incidents"]],
            on="iyear",
            how="outer",
        ).fillna(0).sort_values("iyear")

        fig_bench = go.Figure()
        fig_bench.add_trace(
            go.Scatter(
                x=merged_benchmark["iyear"],
                y=merged_benchmark["country_incidents"],
                name=f"{selected_country} Incidents",
                mode="lines+markers",
                line=dict(color="#00E5FF", width=3),
                marker=dict(size=5),
            )
        )
        fig_bench.add_trace(
            go.Scatter(
                x=merged_benchmark["iyear"],
                y=merged_benchmark["regional_mean_incidents"],
                name=f"Regional Peer Average ({theatre_region})",
                mode="lines",
                line=dict(color="#FFD600", width=2, dash="dash"),
            )
        )

        if selected_years[0] <= MISSING_YEAR <= selected_years[1]:
            fig_bench.add_vrect(
                x0=1992.5,
                x1=1993.5,
                fillcolor="#FF9100",
                opacity=0.25,
                line_dash="dot",
            )

        fig_bench.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#1A1D24",
            xaxis=dict(title="Year", dtick=5, gridcolor="#2B313D"),
            yaxis=dict(title="Annual Incident Volume", gridcolor="#2B313D"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=30, b=40),
            height=380,
        )
        st.plotly_chart(fig_bench, use_container_width=True)
    else:
        st.info("No other sovereign states in this region available for peer benchmarking.")

    st.markdown("---")

    # Section 3: Tactic, Weapon & Target Breakdowns
    st.markdown("### 🎯 Tactical Signatures & Operational Modus Operandi")
    c_targ, c_weap, c_attk = st.columns(3)

    with c_targ:
        st.markdown("#### Target Sectors")
        top_targets = country_df["targtype1_txt"].value_counts().head(7).reset_index()
        top_targets.columns = ["Target", "Count"]
        fig_t = px.pie(
            top_targets,
            values="Count",
            names="Target",
            hole=0.45,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Teal,
        )
        fig_t.update_layout(paper_bgcolor="#0E1117", margin=dict(l=10, r=10, t=10, b=10), height=280)
        st.plotly_chart(fig_t, use_container_width=True)

    with c_weap:
        st.markdown("#### Weapon Classification")
        top_weapons = country_df["weaptype1_txt"].value_counts().head(7).reset_index()
        top_weapons.columns = ["Weapon", "Count"]
        fig_w = px.pie(
            top_weapons,
            values="Count",
            names="Weapon",
            hole=0.45,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Purp,
        )
        fig_w.update_layout(paper_bgcolor="#0E1117", margin=dict(l=10, r=10, t=10, b=10), height=280)
        st.plotly_chart(fig_w, use_container_width=True)

    with c_attk:
        st.markdown("#### Primary Attack Types")
        top_attacks = country_df["attacktype1_txt"].value_counts().head(7).reset_index()
        top_attacks.columns = ["Attack Type", "Count"]
        fig_a = px.pie(
            top_attacks,
            values="Count",
            names="Attack Type",
            hole=0.45,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.OrRd,
        )
        fig_a.update_layout(paper_bgcolor="#0E1117", margin=dict(l=10, r=10, t=10, b=10), height=280)
        st.plotly_chart(fig_a, use_container_width=True)

    st.markdown("---")

    # Section 4: Leading Perpetrators in the Country
    st.markdown(f"### 🏴 Leading Perpetrator Factions in {selected_country}")
    col_grp_chart, col_grp_table = st.columns([1, 1])

    with col_grp_chart:
        country_groups = country_df[country_df["gname"] != UNKNOWN_GROUP_NAME]["gname"].value_counts().head(8).reset_index()
        country_groups.columns = ["Group", "Incidents"]

        if not country_groups.empty:
            fig_cg = px.bar(
                country_groups,
                x="Incidents",
                y="Group",
                orientation="h",
                color="Incidents",
                color_continuous_scale="Reds",
                template="plotly_dark",
            )
            fig_cg.update_layout(
                paper_bgcolor="#0E1117",
                plot_bgcolor="#1A1D24",
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=10, b=20),
                height=320,
            )
            st.plotly_chart(fig_cg, use_container_width=True)
        else:
            st.info("No identified perpetrator groups recorded for this country (all classified as Unknown).")

    with col_grp_table:
        unk_cnt = int((country_df["gname"] == UNKNOWN_GROUP_NAME).sum())
        unk_pct = round(unk_cnt / len(country_df) * 100, 1)
        st.markdown(
            f"""
            - **Unclaimed / Unknown Incidents:** {unk_cnt:,} ({unk_pct}% of total national volume).
            - **Attributed Organizations:** {country_df[country_df['gname'] != UNKNOWN_GROUP_NAME]['gname'].nunique()} unique factions identified.
            - **Tactical Diversity:** {country_df['attacktype1_txt'].nunique()} different attack methods deployed.
            """
        )

    st.markdown("---")

    # Section 5: Deadliest Documented Incidents Dossier
    st.markdown("### 💀 Deadliest Documented Incidents Dossier")
    st.caption("Top 10 highest-fatality attacks recorded within sovereign territory.")

    deadliest_df = (
        country_df.sort_values("nkill", ascending=False)
        .head(10)[[
            "iyear",
            "imonth",
            "iday",
            "city",
            "gname",
            "attacktype1_txt",
            "weaptype1_txt",
            "nkill",
            "nwound",
            "summary",
        ]]
        .copy()
    )

    deadliest_df["Date"] = (
        deadliest_df["iyear"].astype(str)
        + "-"
        + deadliest_df["imonth"].astype(str).str.zfill(2)
        + "-"
        + deadliest_df["iday"].astype(str).str.zfill(2)
    )

    st.dataframe(
        deadliest_df[[
            "Date",
            "city",
            "gname",
            "attacktype1_txt",
            "weaptype1_txt",
            "nkill",
            "nwound",
            "summary",
        ]].rename(columns={
            "city": "City",
            "gname": "Perpetrator Faction",
            "attacktype1_txt": "Tactic",
            "weaptype1_txt": "Weapon",
            "nkill": "Fatalities",
            "nwound": "Wounded",
            "summary": "Intelligence Narrative",
        }),
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()

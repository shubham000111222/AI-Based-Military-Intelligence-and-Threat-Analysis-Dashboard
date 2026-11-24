"""
10_Group_Profiles.py - Threat Group Behavioral Profiles & Tactical Clustering.
Features:
- High-dimensional behavioral vector clustering (KMeans) & 2D PCA projection
- Interactive cluster scatter plot with tactical archetype labels
- Deep group dossier profile card (active lifespan, tactics, targets, lethality, timeline)
- 1993 gap annotation on activity timelines.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import (
    ETHICAL_DISCLAIMER,
    MISSING_YEAR,
    PROCESSED_DATA_PATH,
)
from src.data_loader import load_dataset
from src.groups import cluster_and_project_groups, get_group_dossier

st.set_page_config(
    page_title="Threat Group Profiles | GTD Analysis",
    page_icon="🏴",
    layout="wide",
)


@st.cache_data(show_spinner="Loading Intelligence Dataset...")
def get_data():
    return load_dataset(PROCESSED_DATA_PATH)


def main():
    st.title("10 · Threat Group Behavioral Profiles & Tactical Archetypes")
    st.caption("Unsupervised Behavioral Vector Clustering (KMeans + PCA) & Operational Dossiers")

    st.info(f"**HISTORICAL & RESEARCH DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    df = get_data()

    # Sidebar parameters
    st.sidebar.markdown("### 🎛️ Profiling Parameters")
    min_incidents = st.sidebar.slider(
        "Minimum Incident Qualification Cutoff",
        min_value=10,
        max_value=100,
        value=20,
        step=5,
        help="Groups with fewer recorded attacks than this threshold are excluded from clustering.",
    )
    n_clusters = st.sidebar.slider("Number of Behavioral Clusters (k)", 2, 6, 4)

    # Perform clustering and projection
    groups_df, cluster_names = cluster_and_project_groups(
        df,
        min_incidents=min_incidents,
        n_clusters=n_clusters,
    )

    if groups_df.empty:
        st.warning(f"No militant factions met the cutoff of >= {min_incidents} incidents.")
        st.stop()

    # Section 1: 2D Behavioral Cluster Scatter (PCA)
    st.markdown("### 🧭 2D Behavioral Feature Space (PCA Projection)")
    st.caption(
        f"Synthesized from attack-type distributions, target distributions, regional footprints, and casualty statistics "
        f"across **{len(groups_df)}** qualified factions. Point size denotes total casualties."
    )

    fig_pca = px.scatter(
        groups_df,
        x="pca_x",
        y="pca_y",
        color="cluster_label",
        size="total_casualties",
        size_max=35,
        hover_name="gname",
        hover_data={
            "incidents": True,
            "fatalities": True,
            "primary_country": True,
            "primary_region": True,
            "cluster_label": True,
            "pca_x": False,
            "pca_y": False,
        },
        template="plotly_dark",
        title="Behavioral Vector Clustering of Threat Actors",
    )
    fig_pca.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#1A1D24",
        xaxis=dict(title="Principal Component 1 (Tactical & Regional Variance)", gridcolor="#2B313D"),
        yaxis=dict(title="Principal Component 2 (Lethality & Scale Variance)", gridcolor="#2B313D"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=""),
        margin=dict(l=40, r=40, t=30, b=40),
        height=500,
    )
    st.plotly_chart(fig_pca, use_container_width=True)

    st.markdown("---")

    # Section 2: Deep Group Dossier Card
    st.markdown("### 📋 Sovereign Threat Actor Dossier Card")
    st.caption("Select an individual faction to inspect operational history, weapon profile, and tactical trajectory:")

    all_qualified_groups = sorted(groups_df["gname"].tolist())
    selected_gname = st.selectbox("Select Threat Faction", all_qualified_groups, index=0)

    # Extract dossier
    dossier = get_group_dossier(df, selected_gname)
    group_cluster_info = groups_df[groups_df["gname"] == selected_gname].iloc[0]

    # Dossier Header Card
    st.markdown(
        f"""
        <div style="background-color: #1A1D24; border-left: 5px solid #FF1744; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <div style="font-size: 0.85rem; color: #9E9E9E; text-transform: uppercase;">TACTICAL DOSSIER CLASSIFICATION</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #FAFAFA; margin: 4px 0;">{selected_gname}</div>
            <div style="display: flex; gap: 20px; margin-top: 8px;">
                <span style="color: #00E5FF; font-weight: 600;">Archetype: {group_cluster_info['cluster_label']}</span>
                <span style="color: #FFD600;">Active Lifespan: {dossier['start_year']} – {dossier['end_year']} ({dossier['active_span']} years)</span>
                <span style="color: #E0E0E0;">Primary Theatre: {group_cluster_info['primary_region']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Key Metrics Grid
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("DOCUMENTED INCIDENTS", f"{dossier['total_incidents']:,}")
    with m2:
        st.metric("FATALITIES INFLICTED", f"{dossier['total_fatalities']:,}")
    with m3:
        st.metric("WOUNDED CASUALTIES", f"{dossier['total_wounded']:,}")
    with m4:
        st.metric("LETHALITY (KILLS/INC)", f"{dossier['mean_fatalities_per_inc']}")
    with m5:
        st.metric("ACTIVE YEARS SPAN", f"{dossier['active_years_count']} active yrs")

    st.markdown("<br>", unsafe_allow_html=True)

    # Breakdown Charts: Tactics, Targets, Timeline
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown("#### Primary Attack Tactics Deployment")
        tactics_df = pd.DataFrame(dossier["top_tactics"])
        fig_tac = px.pie(
            tactics_df,
            values="count",
            names="tactic",
            hole=0.45,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Reds,
        )
        fig_tac.update_layout(paper_bgcolor="#0E1117", margin=dict(l=10, r=10, t=10, b=10), height=260)
        st.plotly_chart(fig_tac, use_container_width=True)

    with c_right:
        st.markdown("#### Targeted Strategic Sectors")
        targets_df = pd.DataFrame(dossier["top_targets"])
        fig_tar = px.pie(
            targets_df,
            values="count",
            names="target",
            hole=0.45,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Burg,
        )
        fig_tar.update_layout(paper_bgcolor="#0E1117", margin=dict(l=10, r=10, t=10, b=10), height=260)
        st.plotly_chart(fig_tar, use_container_width=True)

    st.markdown("#### Longitudinal Operational Timeline")
    st.caption("Annual attack frequency and fatalities inflicted over group lifespan:")

    timeline_df = dossier["timeline"]
    fig_time = go.Figure()
    fig_time.add_trace(
        go.Bar(
            x=timeline_df["iyear"],
            y=timeline_df["incidents"],
            name="Incidents",
            marker_color="#37474F",
            yaxis="y1",
        )
    )
    fig_time.add_trace(
        go.Scatter(
            x=timeline_df["iyear"],
            y=timeline_df["fatalities"],
            name="Fatalities",
            mode="lines+markers",
            line=dict(color="#FF1744", width=2.5),
            marker=dict(size=5),
            yaxis="y2",
        )
    )

    if dossier["start_year"] <= MISSING_YEAR <= dossier["end_year"]:
        fig_time.add_vrect(
            x0=1992.5,
            x1=1993.5,
            fillcolor="#FF9100",
            opacity=0.3,
            line_width=1.5,
            line_dash="dash",
            annotation_text="1993 Gap",
            annotation_position="top left",
        )

    fig_time.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#1A1D24",
        xaxis=dict(title="Year", dtick=2, gridcolor="#2B313D"),
        yaxis=dict(title="Annual Incidents", gridcolor="#2B313D"),
        yaxis2=dict(title="Annual Fatalities", overlaying="y", side="right", showgrid=False, color="#FF1744"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=30, b=40),
        height=320,
    )
    st.plotly_chart(fig_time, use_container_width=True)


if __name__ == "__main__":
    main()

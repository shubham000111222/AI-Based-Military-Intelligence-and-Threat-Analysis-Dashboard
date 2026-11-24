"""
02_Global_Threat_Map.py - Geospatial Threat Center & DBSCAN Spatial Hotspot Clusters.
Features:
- Global Plotly threat map with filters (year range, region, attack type, group, min casualties)
- Animated longitudinal year slider
- DBSCAN spatial clustering with haversine distance metric (adjustable eps_km, min_samples)
- Cluster centroid table, casualty summaries, and tactical signature breakdown.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import (
    ETHICAL_DISCLAIMER,
    PROCESSED_DATA_PATH,
    UNKNOWN_GROUP_NAME,
)
from src.data_loader import load_dataset
from src.hotspots import compute_spatial_clusters, filter_valid_coordinates

st.set_page_config(
    page_title="Geospatial Threat Center | GTD Analysis",
    page_icon="🗺️",
    layout="wide",
)


@st.cache_data(show_spinner="Loading Geospatial Intelligence...")
def get_map_data() -> pd.DataFrame:
    return load_dataset(PROCESSED_DATA_PATH)


def main():
    st.title("02 · Geospatial Threat Center & Spatial Hotspot Clusters")
    st.caption("Tactical Incident Mapping & Unsupervised Density Hotspotting (1970–2017)")

    st.info(f"**HISTORICAL & RESEARCH DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    df = get_map_data()
    df_coords = filter_valid_coordinates(df)

    # Sidebar Filter Controls
    st.sidebar.markdown("### 🎛️ Spatial & Tactical Filters")

    min_yr = int(df_coords["iyear"].min())
    max_yr = int(df_coords["iyear"].max())
    selected_years = st.sidebar.slider(
        "Observation Period",
        min_value=min_yr,
        max_value=max_yr,
        value=(max(min_yr, 2000), max_yr),
        step=1,
    )

    regions = ["All Regions"] + sorted(df_coords["region_txt"].dropna().unique().tolist())
    selected_region = st.sidebar.selectbox("Geographic Theatre", regions)

    all_attacks = sorted(df_coords["attacktype1_txt"].dropna().unique().tolist())
    selected_attacks = st.sidebar.multiselect(
        "Attack Types",
        options=all_attacks,
        default=all_attacks[:5] if len(all_attacks) >= 5 else all_attacks,
    )

    groups = ["All Perpetrators"] + sorted([
        g for g in df_coords["gname"].dropna().unique().tolist()
        if g != UNKNOWN_GROUP_NAME
    ])
    selected_group = st.sidebar.selectbox("Perpetrator Faction", groups)

    min_casualties = st.sidebar.slider(
        "Minimum Casualties (Killed + Wounded)",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
    )

    # Filter dataset
    filtered_df = df_coords[
        (df_coords["iyear"] >= selected_years[0])
        & (df_coords["iyear"] <= selected_years[1])
        & (df_coords["ncasualty"] >= min_casualties)
    ]

    if selected_region != "All Regions":
        filtered_df = filtered_df[filtered_df["region_txt"] == selected_region]

    if selected_attacks:
        filtered_df = filtered_df[filtered_df["attacktype1_txt"].isin(selected_attacks)]

    if selected_group != "All Perpetrators":
        filtered_df = filtered_df[filtered_df["gname"] == selected_group]

    # Map Mode Selection
    tab_incident_map, tab_hotspots = st.tabs([
        "📍 Interactive Incident Map & Temporal Animation",
        "🔥 DBSCAN Spatial Hotspot Discovery",
    ])

    with tab_incident_map:
        st.markdown("### Tactical Incident Plotter")
        st.caption(
            f"Displaying **{len(filtered_df):,}** incidents meeting filter criteria. "
            "Marker size reflects casualty magnitude."
        )

        enable_animation = st.checkbox("Enable Animated Annual Progression Slider", value=False)

        if len(filtered_df) == 0:
            st.warning("No incidents matched the selected filter criteria. Please broaden your selection.")
        else:
            # Optimize sample size for smooth webGL rendering if dataset exceeds 5000 points
            render_sample_note = False
            plot_df = filtered_df
            if len(filtered_df) > 5000 and not enable_animation:
                plot_df = filtered_df.sample(n=5000, random_state=42)
                render_sample_note = True

            # Bubble size calculation (clipped for visual balance)
            plot_df = plot_df.copy()
            plot_df["bubble_size"] = plot_df["ncasualty"].apply(lambda c: min(max(c, 2), 40))

            if enable_animation:
                anim_df = filtered_df.sort_values("iyear").copy()
                anim_df["bubble_size"] = anim_df["ncasualty"].apply(lambda c: min(max(c, 2), 35))
                fig_map = px.scatter_geo(
                    anim_df,
                    lat="latitude",
                    lon="longitude",
                    color="attacktype1_txt",
                    size="bubble_size",
                    animation_frame="iyear",
                    hover_name="city",
                    hover_data={
                        "country_txt": True,
                        "gname": True,
                        "nkill": True,
                        "nwound": True,
                        "attacktype1_txt": True,
                        "latitude": False,
                        "longitude": False,
                        "bubble_size": False,
                    },
                    projection="natural earth",
                    template="plotly_dark",
                    title=f"Animated Threat Evolution ({selected_years[0]}–{selected_years[1]})",
                )
            else:
                fig_map = px.scatter_geo(
                    plot_df,
                    lat="latitude",
                    lon="longitude",
                    color="attacktype1_txt",
                    size="bubble_size",
                    hover_name="city",
                    hover_data={
                        "country_txt": True,
                        "gname": True,
                        "nkill": True,
                        "nwound": True,
                        "attacktype1_txt": True,
                        "latitude": False,
                        "longitude": False,
                        "bubble_size": False,
                    },
                    projection="natural earth",
                    template="plotly_dark",
                    title="Geospatial Incident Coordinates",
                )

            fig_map.update_geos(
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
            fig_map.update_layout(
                paper_bgcolor="#0E1117",
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    title_text="",
                ),
                height=600,
            )
            st.plotly_chart(fig_map, use_container_width=True)

            if render_sample_note:
                st.caption("ℹ️ *Displaying a representative 5,000 incident sample for optimal client rendering performance.*")

    with tab_hotspots:
        st.markdown("### DBSCAN Haversine Spatial Cluster Detection")
        st.markdown(
            "Identifies high-density geographic incident concentrations using **DBSCAN** "
            "with a spherical **haversine metric**. Points within distance $\\varepsilon$ forming cores "
            "of at least $N_{min}$ incidents are synthesized into tactical activity hotspots."
        )

        h_col1, h_col2 = st.columns(2)
        with h_col1:
            eps_km = st.slider(
                "Cluster Neighborhood Radius (ε in km)",
                min_value=15.0,
                max_value=300.0,
                value=75.0,
                step=5.0,
                help="Maximum spherical geodesic distance between incidents to form a cluster.",
            )
        with h_col2:
            min_samples = st.slider(
                "Minimum Incident Core Size (min_samples)",
                min_value=5,
                max_value=50,
                value=12,
                step=1,
                help="Minimum number of incidents required to initialize an active cluster core.",
            )

        if len(filtered_df) < min_samples:
            st.warning("Insufficient incidents in current filter selection to form DBSCAN clusters.")
        else:
            with st.spinner("Computing spherical haversine density clusters..."):
                clustered_df, cluster_summary = compute_spatial_clusters(
                    filtered_df,
                    eps_km=eps_km,
                    min_samples=min_samples,
                )

            n_clusters = len(cluster_summary)
            core_points = (clustered_df["cluster_id"] >= 0).sum()
            noise_points = (clustered_df["cluster_id"] == -1).sum()
            clustered_share = round(float(core_points / len(clustered_df) * 100), 1)

            st.markdown("#### Hotspot Discovery Telemetry")
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("IDENTIFIED HOTSPOTS", f"{n_clusters} clusters")
            with m2:
                st.metric("CLUSTERED INCIDENTS", f"{core_points:,}")
            with m3:
                st.metric("DISPERSED NOISE", f"{noise_points:,}")
            with m4:
                st.metric("CLUSTER DENSITY RATIO", f"{clustered_share}%")

            if n_clusters > 0:
                # Plot Hotspot Centroids and Clustered Points
                st.markdown("#### Hotspot Geospatial Map")
                show_noise = st.checkbox("Show Dispersed Noise Incidents (Greyed)", value=False)

                map_sub = clustered_df if show_noise else clustered_df[clustered_df["cluster_id"] >= 0]
                map_sub = map_sub.copy()
                map_sub["Cluster Label"] = map_sub["cluster_id"].apply(
                    lambda cid: "Noise Outlier" if cid == -1 else f"Cluster #{cid}"
                )

                fig_cluster_map = px.scatter_geo(
                    map_sub,
                    lat="latitude",
                    lon="longitude",
                    color="Cluster Label",
                    hover_name="city",
                    hover_data={
                        "country_txt": True,
                        "gname": True,
                        "ncasualty": True,
                        "Cluster Label": True,
                        "latitude": False,
                        "longitude": False,
                    },
                    template="plotly_dark",
                    projection="natural earth",
                    title=f"DBSCAN Spatial Hotspot Clusters (ε={eps_km} km, min_samples={min_samples})",
                )
                fig_cluster_map.update_geos(
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
                fig_cluster_map.update_layout(
                    paper_bgcolor="#0E1117",
                    margin=dict(l=0, r=0, t=40, b=0),
                    height=550,
                )
                st.plotly_chart(fig_cluster_map, use_container_width=True)

                st.markdown("#### Ranked Hotspot Directory")
                st.dataframe(
                    cluster_summary[[
                        "cluster_id",
                        "incident_count",
                        "total_fatalities",
                        "total_casualties",
                        "centroid_lat",
                        "centroid_lon",
                        "primary_country",
                        "primary_region",
                        "primary_attack_type",
                        "primary_group",
                        "year_range",
                    ]].rename(columns={
                        "cluster_id": "Cluster #",
                        "incident_count": "Incidents",
                        "total_fatalities": "Fatalities",
                        "total_casualties": "Total Casualties",
                        "centroid_lat": "Centroid Lat",
                        "centroid_lon": "Centroid Lon",
                        "primary_country": "Country",
                        "primary_region": "Theatre",
                        "primary_attack_type": "Dominant Tactic",
                        "primary_group": "Dominant Group",
                        "year_range": "Active Years",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info(
                    "No dense spatial clusters found with the current ε and min_samples thresholds. "
                    "Try increasing the neighborhood radius (ε) or lowering min_samples."
                )


if __name__ == "__main__":
    main()

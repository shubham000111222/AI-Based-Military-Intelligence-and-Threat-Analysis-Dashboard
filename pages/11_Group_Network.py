"""
11_Group_Network.py - Militant Group Relational Network & Modularity Graph.
Features:
- Multi-modal graph construction: Co-Claims, Shared Target Profiles, and Shared Regional Footprints
- Interactive 2D Spring-Layout NetworkX graph rendered in Plotly
- Network centrality analytics (Degree Centrality & Betweenness Centrality)
- Greedy modularity community detection
- Prominent operational caption clarifying edges show similarity/co-claims, not proven alliance.
"""

import networkx as nx
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from src.config import (
    ETHICAL_DISCLAIMER,
    PROCESSED_DATA_PATH,
)
from src.data_loader import load_dataset
from src.network import (
    NETWORK_AFFILIATION_CAVEAT,
    build_group_network,
)

st.set_page_config(
    page_title="Group Operational Network | GTD Analysis",
    page_icon="🕸️",
    layout="wide",
)


@st.cache_data(show_spinner="Loading Intelligence Dataset...")
def get_data():
    return load_dataset(PROCESSED_DATA_PATH)


def main():
    st.title("11 · Terrorist Group Operational Network & Relational Graph")
    st.caption("Topological Network Analysis Across Co-Attributions and Tactical Modus Operandi Similarities")

    st.info(f"**HISTORICAL & RESEARCH DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    # Mandatory Affiliation Caveat Banner
    st.warning(f"⚠️ **{NETWORK_AFFILIATION_CAVEAT}**")

    df = get_data()

    # Sidebar Controls
    st.sidebar.markdown("### 🎛️ Network Topology Controls")

    edge_mode_labels = {
        "Shared Target Sectors (Cosine Similarity)": "shared_targets",
        "Shared Regional Theatres (Cosine Similarity)": "shared_regions",
        "Co-Claimed Attacks (gname2 / gname3)": "co_claim",
    }

    selected_mode_label = st.sidebar.selectbox("Relational Modality (Edge Type)", list(edge_mode_labels.keys()), index=0)
    edge_mode = edge_mode_labels[selected_mode_label]

    min_incidents = st.sidebar.slider(
        "Minimum Incident Volume for Node Qualification",
        min_value=10,
        max_value=80,
        value=15,
        step=5,
    )

    if edge_mode == "co_claim":
        sim_thresh = st.sidebar.slider("Minimum Co-Claimed Attacks", min_value=1, max_value=10, value=1, step=1)
    else:
        sim_thresh = st.sidebar.slider("Edge Similarity Threshold (Cosine)", min_value=0.30, max_value=0.95, value=0.60, step=0.05)

    # Build Network Graph
    with st.spinner("Constructing topological graph and calculating centrality metrics..."):
        G, node_df = build_group_network(
            df,
            edge_type=edge_mode,
            similarity_threshold=sim_thresh,
            min_incidents=min_incidents,
        )

    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()

    # Telemetry KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("NETWORK NODES (GROUPS)", f"{num_nodes}")
    with k2:
        st.metric("RELATIONAL EDGES", f"{num_edges}")
    with k3:
        n_comm = node_df["community_id"].nunique() if not node_df.empty else 0
        st.metric("IDENTIFIED COMMUNITIES", f"{n_comm}")
    with k4:
        density = round(float(nx.density(G)), 4) if num_nodes > 1 else 0.0
        st.metric("NETWORK DENSITY", f"{density}")

    st.markdown("---")

    # Section 1: Plotly Network Visualizer
    st.markdown(f"### 🕸️ Topological Graph: **{selected_mode_label}**")
    st.caption("Node size denotes incident scale; node color represents detected community partition:")

    if num_nodes == 0 or num_edges == 0:
        st.info("No network edges formed at the selected similarity threshold. Try lowering the threshold slider.")
    else:
        # Generate Fruchterman-Reingold spring layout
        pos = nx.spring_layout(G, k=0.35, iterations=50, seed=42)

        # Build Edge Line Traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color="rgba(144, 164, 174, 0.3)"),
            hoverinfo="none",
            mode="lines",
            showlegend=False,
        )

        # Build Node Traces
        node_x = []
        node_y = []
        node_text = []
        node_sizes = []
        node_colors = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            n_meta = node_df[node_df["gname"] == node].iloc[0]
            comm_id = n_meta["community_id"]
            deg = n_meta["degree_centrality"]
            bet = n_meta["betweenness_centrality"]
            inc = n_meta["incidents"]
            reg = n_meta["primary_region"]

            hover_html = (
                f"<b>{node}</b><br>"
                f"Primary Theatre: {reg}<br>"
                f"Documented Attacks: {inc:,}<br>"
                f"Degree Centrality: {deg:.3f}<br>"
                f"Betweenness Centrality: {bet:.3f}<br>"
                f"Community Cluster: #{comm_id}"
            )
            node_text.append(hover_html)
            # Size scale
            node_sizes.append(max(10, min(int(np.sqrt(inc) * 3), 40)))
            node_colors.append(comm_id)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=[n if G.nodes[n]["incidents"] > 30 else "" for n in G.nodes()],
            textposition="top center",
            textfont=dict(size=9, color="#FAFAFA"),
            hovertext=node_text,
            marker=dict(
                showscale=True,
                colorscale="Viridis",
                color=node_colors,
                size=node_sizes,
                colorbar=dict(
                    thickness=12,
                    title=dict(text="Community", font=dict(color="#FAFAFA")),
                    xanchor="left",
                    titleside="right",
                ),
                line=dict(width=1.5, color="#2B313D"),
            ),
            showlegend=False,
        )

        fig_net = go.Figure(data=[edge_trace, node_trace])
        fig_net.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            margin=dict(l=10, r=10, t=20, b=20),
            height=600,
        )
        st.plotly_chart(fig_net, use_container_width=True)

    st.markdown("---")

    # Section 2: Centrality Leaderboard & Community Breakdown
    c_cent, c_comm = st.columns([1, 1])

    with c_cent:
        st.markdown("### 🏆 Tactical Centrality Leaderboard")
        st.caption("Identifies structural hubs (Degree) and strategic brokers (Betweenness):")

        st.dataframe(
            node_df[[
                "gname",
                "primary_region",
                "incidents",
                "degree_centrality",
                "betweenness_centrality",
                "community_id",
            ]].rename(columns={
                "gname": "Threat Faction",
                "primary_region": "Primary Region",
                "incidents": "Attacks",
                "degree_centrality": "Degree Cent.",
                "betweenness_centrality": "Betweenness Cent.",
                "community_id": "Community",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with c_comm:
        st.markdown("### 🏘️ Detected Community Partitions")
        st.caption("Modularity groupings sharing tight tactical or regional linkages:")

        if not node_df.empty:
            for cid, grp in node_df.groupby("community_id"):
                members = grp["gname"].tolist()
                top_reg = grp["primary_region"].mode()[0] if not grp["primary_region"].empty else "Mixed"
                with st.expander(f"Community Cluster #{cid} ({len(members)} Factions) — Focus: {top_reg}", expanded=False):
                    st.write(", ".join(members))
        else:
            st.info("No communities identified.")


if __name__ == "__main__":
    main()

"""
Network graph construction and topological analysis for militant groups.
Constructs NetworkX relational graphs across three distinct modalities:
1. Co-claimed attacks: Co-attributions recorded in secondary/tertiary claim fields (gname2, gname3)
2. Shared target profiles: Cosine similarity of target sector distributions
3. Shared regional footprint: Cosine similarity of geographic theatre distributions
Computes degree centrality, betweenness centrality, and greedy modularity community detection.
"""

import logging
from typing import Dict, Tuple

import networkx as nx
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.config import UNKNOWN_GROUP_NAME

logger = logging.getLogger(__name__)

# Mandatory operational disclaimer regarding relational inferences
NETWORK_AFFILIATION_CAVEAT: str = (
    "ANALYTICAL NOTICE: Graph edges reflect statistical behavioral similarity or co-claimed "
    "incidents in historical archives, NOT verified tactical alliance, mutual command, or "
    "operational coordination."
)


def build_group_network(
    df: pd.DataFrame,
    edge_type: str = "shared_targets",  # 'co_claim', 'shared_targets', 'shared_regions'
    similarity_threshold: float = 0.50,
    min_incidents: int = 15,
) -> Tuple[nx.Graph, pd.DataFrame]:
    """
    Construct NetworkX graph of militant groups based on co-claims or tactical cosine similarity.

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame.
    edge_type : str
        Type of relationship: 'co_claim', 'shared_targets', 'shared_regions'.
    similarity_threshold : float
        Minimum cosine similarity (or incident count for co-claim) to generate an edge.
    min_incidents : int
        Minimum incident volume for node inclusion (default: 15).

    Returns
    -------
    Tuple[nx.Graph, pd.DataFrame]
        1. G: Populated NetworkX Graph.
        2. node_table: DataFrame summarizing centrality metrics and community assignments.
    """
    # Filter valid groups
    known_mask = (df["gname"] != UNKNOWN_GROUP_NAME) & (df["gname"].notna()) & (df["gname"] != "")
    known_df = df[known_mask].copy()

    counts = known_df["gname"].value_counts()
    valid_groups = counts[counts >= min_incidents].index.tolist()

    if len(valid_groups) == 0:
        valid_groups = counts.head(10).index.tolist()

    sub = known_df[known_df["gname"].isin(valid_groups)].copy()

    G = nx.Graph()

    # 1. Add Nodes with Metadata
    for g in valid_groups:
        g_sub = sub[sub["gname"] == g]
        tot_inc = len(g_sub)
        tot_kill = int(g_sub["nkill"].sum())
        top_reg = g_sub["region_txt"].mode()[0] if not g_sub["region_txt"].empty else "Unknown"
        top_attk = g_sub["attacktype1_txt"].mode()[0] if not g_sub["attacktype1_txt"].empty else "Unknown"

        G.add_node(
            g,
            incidents=tot_inc,
            fatalities=tot_kill,
            primary_region=top_reg,
            primary_attack=top_attk,
        )

    # 2. Add Edges according to selected modality
    if edge_type == "co_claim":
        # Extract co-claimed incidents where gname2 or gname3 matches valid groups
        co_counts: Dict[Tuple[str, str], int] = {}
        for _, row in sub.iterrows():
            g1 = row["gname"]
            for col in ["gname2", "gname3"]:
                g2 = row.get(col, None)
                if g2 and g2 in valid_groups and g2 != g1:
                    edge_key = tuple(sorted([g1, g2]))
                    co_counts[edge_key] = co_counts.get(edge_key, 0) + 1

        # Add edges meeting threshold
        min_co_claims = max(1, int(similarity_threshold))
        for (g1, g2), weight in co_counts.items():
            if weight >= min_co_claims:
                G.add_edge(g1, g2, weight=weight, sim=weight)

    elif edge_type == "shared_targets":
        # Cosine similarity on target sector vectors
        targ_matrix = pd.crosstab(sub["gname"], sub["targtype1_txt"], normalize="index").reindex(valid_groups, fill_value=0.0)
        sim_mat = cosine_similarity(targ_matrix.values)

        for i in range(len(valid_groups)):
            for j in range(i + 1, len(valid_groups)):
                sim = float(sim_mat[i, j])
                if sim >= similarity_threshold:
                    G.add_edge(valid_groups[i], valid_groups[j], weight=round(sim, 3), sim=round(sim, 3))

    elif edge_type == "shared_regions":
        # Cosine similarity on geographic region vectors
        reg_matrix = pd.crosstab(sub["gname"], sub["region_txt"], normalize="index").reindex(valid_groups, fill_value=0.0)
        sim_mat = cosine_similarity(reg_matrix.values)

        for i in range(len(valid_groups)):
            for j in range(i + 1, len(valid_groups)):
                sim = float(sim_mat[i, j])
                if sim >= similarity_threshold:
                    G.add_edge(valid_groups[i], valid_groups[j], weight=round(sim, 3), sim=round(sim, 3))

    # 3. Centrality Metrics
    if len(G) > 1:
        deg_cent = nx.degree_centrality(G)
        bet_cent = nx.betweenness_centrality(G)
    else:
        deg_cent = {n: 0.0 for n in G.nodes()}
        bet_cent = {n: 0.0 for n in G.nodes()}

    # 4. Community Detection (Greedy Modularity)
    communities_map: Dict[str, int] = {}
    if len(G) > 1 and G.number_of_edges() > 0:
        try:
            communities = list(nx.community.greedy_modularity_communities(G))
            for cid, comm in enumerate(communities):
                for node in comm:
                    communities_map[node] = cid
        except Exception:
            communities_map = {node: 0 for node in G.nodes()}
    else:
        communities_map = {node: 0 for node in G.nodes()}

    # Build Summary Table
    node_records = []
    for node in G.nodes():
        node_records.append({
            "gname": node,
            "incidents": G.nodes[node]["incidents"],
            "fatalities": G.nodes[node]["fatalities"],
            "primary_region": G.nodes[node]["primary_region"],
            "primary_attack": G.nodes[node]["primary_attack"],
            "degree_centrality": round(float(deg_cent.get(node, 0.0)), 4),
            "betweenness_centrality": round(float(bet_cent.get(node, 0.0)), 4),
            "community_id": int(communities_map.get(node, 0)),
        })

    node_df = pd.DataFrame(node_records).sort_values("betweenness_centrality", ascending=False).reset_index(drop=True)
    return G, node_df

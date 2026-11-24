"""
Unit tests for network.py militant group graph construction and centrality.
"""

import networkx as nx

from src.network import (
    NETWORK_AFFILIATION_CAVEAT,
    build_group_network,
)


def test_build_group_network_shared_targets(synthetic_multidecade_df):
    """Verify network construction using shared target profile similarity."""
    G, node_df = build_group_network(
        synthetic_multidecade_df,
        edge_type="shared_targets",
        similarity_threshold=0.40,
        min_incidents=10,
    )

    assert isinstance(G, nx.Graph)
    assert len(G.nodes) > 0
    assert len(node_df) == len(G.nodes)

    # Check centrality columns
    assert "degree_centrality" in node_df.columns
    assert "betweenness_centrality" in node_df.columns
    assert "community_id" in node_df.columns

    # Centrality values must be in [0, 1]
    assert (node_df["degree_centrality"] >= 0.0).all()
    assert (node_df["degree_centrality"] <= 1.0).all()
    assert (node_df["betweenness_centrality"] >= 0.0).all()
    assert (node_df["betweenness_centrality"] <= 1.0).all()


def test_build_group_network_shared_regions(synthetic_multidecade_df):
    """Verify network construction using shared regional footprint similarity."""
    G, node_df = build_group_network(
        synthetic_multidecade_df,
        edge_type="shared_regions",
        similarity_threshold=0.40,
        min_incidents=10,
    )

    assert isinstance(G, nx.Graph)
    assert len(G.nodes) > 0


def test_build_group_network_threshold_filtering(synthetic_multidecade_df):
    """Verify increasing similarity threshold reduces edge density."""
    G_low, _ = build_group_network(
        synthetic_multidecade_df,
        edge_type="shared_targets",
        similarity_threshold=0.30,
        min_incidents=10,
    )
    G_high, _ = build_group_network(
        synthetic_multidecade_df,
        edge_type="shared_targets",
        similarity_threshold=0.85,
        min_incidents=10,
    )

    # High threshold should have fewer or equal edges
    assert G_high.number_of_edges() <= G_low.number_of_edges()


def test_network_affiliation_caveat_string():
    """Verify mandatory operational caveat string contains required legal clarification."""
    assert "NOT verified tactical alliance" in NETWORK_AFFILIATION_CAVEAT

"""
Additional targeted unit tests to achieve >= 85% test coverage across all src modules.
"""

import numpy as np
import pandas as pd
import pytest

from src.data_loader import (
    clean_coordinates,
    clean_text_and_categorical,
    collapse_rare_categories,
    normalise_group_names,
)
from src.data_quality import (
    get_1993_gap_info,
    get_reporting_bias_context,
)
from src.models import evaluate_model, get_candidate_models
from src.network import (
    NETWORK_AFFILIATION_CAVEAT,
    build_group_network,
)
from src.query_engine import (
    execute_query_spec,
    synthesize_answer,
    validate_query_spec,
)
from src.text_mining import (
    compute_dense_embeddings,
    get_topic_prevalence_by_region,
    get_topic_prevalence_over_time,
    search_similar_incidents,
)


@pytest.fixture
def mini_test_df() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "iyear": 2010,
            "imonth": 1,
            "iday": 1,
            "country_txt": "Country A",
            "region_txt": "Region A",
            "provstate": "Province A",
            "city": "City A",
            "attacktype1_txt": "Bombing/Explosion",
            "targtype1_txt": "Military",
            "weaptype1_txt": "Explosives",
            "gname": "Group 1",
            "gname2": "Group 2",
            "gname3": None,
            "nkill": 10,
            "nwound": 20,
            "ncasualty": 30,
            "casualties_known": True,
            "success": 1,
            "suicide": 1,
            "summary": "Militants conducted a major coordinated explosion near the headquarters.",
        },
        {
            "iyear": 2011,
            "imonth": 2,
            "iday": 2,
            "country_txt": "Country B",
            "region_txt": "Region B",
            "provstate": "Province B",
            "city": "City B",
            "attacktype1_txt": "Armed Assault",
            "targtype1_txt": "Police",
            "weaptype1_txt": "Firearms",
            "gname": "Group 2",
            "gname2": None,
            "gname3": None,
            "nkill": 5,
            "nwound": 5,
            "ncasualty": 10,
            "casualties_known": True,
            "success": 1,
            "suicide": 0,
            "summary": "Armed assailants attacked a police station with automatic rifles.",
        },
        {
            "iyear": 2012,
            "imonth": 3,
            "iday": 3,
            "country_txt": "Country A",
            "region_txt": "Region A",
            "provstate": "Province A",
            "city": "City A",
            "attacktype1_txt": "Facility/Infrastructure Attack",
            "targtype1_txt": "Business",
            "weaptype1_txt": "Incendiary",
            "gname": "Group 1",
            "gname2": None,
            "gname3": None,
            "nkill": 0,
            "nwound": 2,
            "ncasualty": 2,
            "casualties_known": True,
            "success": 0,
            "suicide": 0,
            "summary": "Arson attack on local commercial facility causing light damage.",
        },
    ])


def test_models_evaluate_comprehensive():
    y_true = np.array(["Bombing", "Assault", "Bombing", "Assault"])
    y_pred = np.array(["Bombing", "Assault", "Assault", "Assault"])
    classes = ["Assault", "Bombing"]
    y_proba = np.array([
        [0.1, 0.9],
        [0.8, 0.2],
        [0.6, 0.4],
        [0.9, 0.1],
    ])
    regions = pd.Series(["Region A", "Region A", "Region B", "Region B"])

    metrics = evaluate_model(
        model_name="TestModel",
        y_true=y_true,
        y_pred=y_pred,
        y_proba=y_proba,
        classes=classes,
        regions=regions,
    )
    assert metrics["model_name"] == "TestModel"
    assert "accuracy" in metrics
    assert "macro_f1" in metrics
    assert "calibration_curves" in metrics
    assert "per_region_macro_f1" in metrics

    # Test candidate models factory
    candidates = get_candidate_models(42)
    assert "Baseline (Majority Class)" in candidates
    assert "Logistic Regression" in candidates
    assert "Random Forest" in candidates
    assert "LightGBM" in candidates


def test_query_engine_operators_and_metrics(mini_test_df):
    # Test operator >
    spec_gt = {
        "filters": [{"column": "nkill", "op": ">", "value": 4}],
        "group_by": "country_txt",
        "metric": "count",
    }
    res_gt, _ = execute_query_spec(spec_gt, mini_test_df)
    assert len(res_gt) == 2

    # Test operator < and <=
    spec_lt = {
        "filters": [{"column": "nkill", "op": "<=", "value": 5}],
        "group_by": "country_txt",
        "metric": "mean",
        "metric_column": "nkill",
        "sort": "asc",
    }
    res_lt, _ = execute_query_spec(spec_lt, mini_test_df)
    assert len(res_lt) > 0

    # Test operator in and between
    spec_in = {
        "filters": [
            {"column": "country_txt", "op": "in", "value": ["Country A"]},
            {"column": "iyear", "op": "between", "value": [2010, 2012]},
        ],
        "group_by": None,
        "metric": "count",
        "top_n": 5,
    }
    res_in, _ = execute_query_spec(spec_in, mini_test_df)
    assert len(res_in) == 2

    # Test validation failures
    assert not validate_query_spec("not a dict")[0]
    assert not validate_query_spec({"filters": "not a list"})[0]
    assert not validate_query_spec({"filters": ["not a dict"]})[0]
    assert not validate_query_spec({"filters": [], "metric": "unauthorized"})[0]
    assert not validate_query_spec({"filters": [], "metric_column": "country_txt"})[0]
    assert not validate_query_spec({"filters": [], "group_by": 12345})[0]

    # Synthesize answer for empty dataframe
    ans_empty = synthesize_answer({"group_by": "country_txt"}, pd.DataFrame(), "What is Country X?")
    assert "No historical incidents match" in ans_empty


def test_network_co_claim_and_communities(mini_test_df):
    G, node_df = build_group_network(mini_test_df, edge_type="co_claim", min_incidents=1)
    assert G.number_of_nodes() >= 2
    assert G.has_edge("Group 1", "Group 2")
    assert "community_id" in node_df.columns
    assert "degree_centrality" in node_df.columns
    assert NETWORK_AFFILIATION_CAVEAT is not None


def test_text_mining_string_similarity_search():
    texts = [
        "Car bomb explosion targeting a hotel.",
        "Armed militants ambushed a military patrol.",
        "Ransom kidnapping of private executives.",
    ]
    emb, vec, svd = compute_dense_embeddings(texts, dim=16, random_state=42)
    meta_df = pd.DataFrame({
        "clean_summary": texts,
        "country_txt": ["Country A", "Country B", "Country C"],
    })

    # Search via custom string query
    res = search_similar_incidents(
        query="Vehicle bombing at hospitality center",
        embeddings=emb,
        meta_df=meta_df,
        top_k=2,
        vectorizer=vec,
        svd=svd,
    )
    assert len(res) == 2
    assert "similarity_score" in res.columns

    # Test empty / edge cases
    assert len(search_similar_incidents("   ", emb, meta_df)) == 0
    assert len(get_topic_prevalence_over_time(pd.DataFrame())) == 0
    assert len(get_topic_prevalence_by_region(pd.DataFrame())) == 0


def test_data_loader_helpers():
    df = pd.DataFrame({
        "latitude": [10.5, 999.0, np.nan, 12.0, 14.0, 16.0],
        "longitude": [20.5, 50.0, np.nan, 22.0, 24.0, 26.0],
        "category": ["A", "A", "A", "A", "Rare", "Rare2"],
        "gname": ["ISIS", "ISIL", "Unknown", "Al-Qaida", "Custom", "Custom2"],
    })
    cleaned_coords = clean_coordinates(df)
    assert pd.isna(cleaned_coords.loc[1, "latitude"])
    assert pd.isna(cleaned_coords.loc[1, "longitude"])

    collapsed = collapse_rare_categories(df, columns=["category"], min_freq=0.25)
    assert "Other" in collapsed["category"].values

    normalised_groups = normalise_group_names(df)
    assert "Islamic State of Iraq and the Levant (ISIL)" in normalised_groups["gname"].values

    cleaned_cat = clean_text_and_categorical(df)
    assert "gname" in cleaned_cat.columns


def test_data_quality_info_methods():
    gap_info = get_1993_gap_info()
    assert "1993" in str(gap_info)

    bias_info = get_reporting_bias_context()
    assert len(bias_info) > 0
    assert "dimension" in bias_info[0]

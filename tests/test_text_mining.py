"""
Unit tests for Phase 8: Incident narrative text mining, topic modeling,
named entity extraction, and semantic vector similarity search.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

from src.text_mining import (
    clean_summary_text,
    compute_dense_embeddings,
    extract_named_entities,
    fit_nmf_topics,
    get_topic_prevalence_by_region,
    get_topic_prevalence_over_time,
    prepare_text_corpus,
    search_similar_incidents,
)


@pytest.fixture
def sample_narrative_df() -> pd.DataFrame:
    """Creates a sample DataFrame of incident narratives for testing."""
    data = [
        {
            "iyear": 2010,
            "region_txt": "Middle East & North Africa",
            "country_txt": "Iraq",
            "summary": "Suspected Al-Qaida militants detonated a car bomb outside a police station in Baghdad.",
            "attacktype1_txt": "Bombing/Explosion",
            "targtype1_txt": "Police",
            "weaptype1_txt": "Explosives",
            "gname": "Al-Qaida",
            "nkill": 5,
            "nwound": 12,
        },
        {
            "iyear": 2010,
            "region_txt": "Middle East & North Africa",
            "country_txt": "Iraq",
            "summary": "An improvised explosive device struck an Iraqi Army military convoy on the highway.",
            "attacktype1_txt": "Bombing/Explosion",
            "targtype1_txt": "Military",
            "weaptype1_txt": "Explosives",
            "gname": "Unknown",
            "nkill": 2,
            "nwound": 4,
        },
        {
            "iyear": 2011,
            "region_txt": "South Asia",
            "country_txt": "Afghanistan",
            "summary": "Taliban insurgents launched an armed assault on a district government center in Kandahar.",
            "attacktype1_txt": "Armed Assault",
            "targtype1_txt": "Government (General)",
            "weaptype1_txt": "Firearms",
            "gname": "Taliban",
            "nkill": 8,
            "nwound": 3,
        },
        {
            "iyear": 2011,
            "region_txt": "South Asia",
            "country_txt": "Afghanistan",
            "summary": "Militants opened fire on a security checkpoint, killing three police officers.",
            "attacktype1_txt": "Armed Assault",
            "targtype1_txt": "Police",
            "weaptype1_txt": "Firearms",
            "gname": "Taliban",
            "nkill": 3,
            "nwound": 1,
        },
        {
            "iyear": 2012,
            "region_txt": "Sub-Saharan Africa",
            "country_txt": "Nigeria",
            "summary": "Boko Haram extremists attacked a rural village church using automatic rifles and petrol bombs.",
            "attacktype1_txt": "Armed Assault",
            "targtype1_txt": "Religious Figures/Institutions",
            "weaptype1_txt": "Firearms",
            "gname": "Boko Haram",
            "nkill": 15,
            "nwound": 20,
        },
        {
            "iyear": 2012,
            "region_txt": "Sub-Saharan Africa",
            "country_txt": "Nigeria",
            "summary": "Short",  # Too short, should be filtered out
            "attacktype1_txt": "Armed Assault",
            "targtype1_txt": "Private Citizens & Property",
            "weaptype1_txt": "Firearms",
            "gname": "Boko Haram",
            "nkill": 1,
            "nwound": 0,
        },
    ]
    return pd.DataFrame(data)


def test_clean_summary_text():
    # Regular text
    raw = "  Militants attacked a checkpoint [source: Reuters]. <br> "
    cleaned = clean_summary_text(raw)
    assert "Reuters" not in cleaned
    assert "<br>" not in cleaned
    assert cleaned.startswith("Militants")

    # Short / invalid text
    assert clean_summary_text("Too short") == ""
    assert clean_summary_text(None) == ""
    assert clean_summary_text(12345) == ""


def test_prepare_text_corpus(sample_narrative_df):
    corpus = prepare_text_corpus(sample_narrative_df, text_col="summary")
    # Row with "Short" should be dropped
    assert len(corpus) == 5
    assert "clean_summary" in corpus.columns
    assert all(len(s) >= 15 for s in corpus["clean_summary"])


def test_fit_nmf_topics(sample_narrative_df):
    corpus = prepare_text_corpus(sample_narrative_df, text_col="summary")
    nmf_model, vectorizer, topic_info, enriched_df = fit_nmf_topics(
        corpus,
        text_col="clean_summary",
        n_topics=3,
        max_features=100,
        random_state=42,
    )
    assert isinstance(nmf_model, NMF)
    assert isinstance(vectorizer, TfidfVectorizer)
    assert len(topic_info) <= 3
    assert len(topic_info) >= 1
    assert "dominant_topic" in enriched_df.columns
    assert "dominant_topic_label" in enriched_df.columns
    assert len(enriched_df) == len(corpus)


def test_topic_prevalence(sample_narrative_df):
    corpus = prepare_text_corpus(sample_narrative_df, text_col="summary")
    _, _, _, enriched_df = fit_nmf_topics(corpus, text_col="clean_summary", n_topics=2)

    time_prev = get_topic_prevalence_over_time(enriched_df)
    assert "iyear" in time_prev.columns
    assert len(time_prev) > 0

    reg_prev = get_topic_prevalence_by_region(enriched_df)
    assert "region_txt" in reg_prev.columns
    assert len(reg_prev) > 0


def test_extract_named_entities():
    texts = [
        "President Obama visited Baghdad in Iraq where General Petraeus met with the Iraqi Police.",
        "Taliban militants attacked Kabul and claimed responsibility against NATO forces.",
        "Boko Haram attacked Abuja near the Ministry of Defence.",
    ]
    entities = extract_named_entities(texts, max_docs=10, top_n=5)
    assert "GPE" in entities
    assert "ORG" in entities
    assert "PERSON" in entities
    assert isinstance(entities["GPE"], list)
    assert isinstance(entities["ORG"], list)
    assert isinstance(entities["PERSON"], list)


def test_compute_dense_embeddings():
    texts = [
        "Bombing incident in urban center.",
        "Armed assault on security forces.",
        "Hostage situation at local bank.",
        "Arson attack on government building.",
    ]
    embeddings, enc, svd = compute_dense_embeddings(texts, dim=16, random_state=42)
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape[0] == 4
    assert embeddings.shape[1] > 0
    # Test L2 normalization
    norms = np.linalg.norm(embeddings, axis=1)
    np.testing.assert_allclose(norms, 1.0, atol=1e-4)


def test_search_similar_incidents():
    # 4 distinct embeddings
    embeddings = np.array([
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=np.float32)
    # Normalize rows
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    meta_df = pd.DataFrame({
        "iyear": [2001, 2002, 2003, 2004],
        "country_txt": ["Country A", "Country B", "Country C", "Country D"],
        "clean_summary": ["Incident 0", "Incident 1", "Incident 2", "Incident 3"],
    })

    # Query by index: index 0 should have index 1 as most similar
    results = search_similar_incidents(query=0, embeddings=embeddings, meta_df=meta_df, top_k=2)
    assert len(results) == 2
    # Self should be excluded
    assert 0 not in results.index
    # First match should be index 1
    assert results.index[0] == 1
    assert results.iloc[0]["similarity_score"] > 0.8

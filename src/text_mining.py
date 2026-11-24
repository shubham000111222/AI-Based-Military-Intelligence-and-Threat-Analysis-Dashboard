"""
Text mining and natural language processing module for incident narrative intelligence.
Provides:
  - Cleaning and filtering of GTD summary narratives.
  - Unsupervised topic modeling via TF-IDF + Non-Negative Matrix Factorization (NMF).
  - Longitudinal and regional topic prevalence analysis.
  - Named Entity Recognition (NER) for GPE, ORG, and PERSON entities with resilient fallback.
  - Semantic vector similarity search over incident narrative embeddings.
"""

import logging
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

# Minimum character length to consider an incident summary meaningful
MIN_SUMMARY_LEN: int = 15

# Stopwords specific to GTD incident narrative boilerplate
GTD_TEXT_STOPWORDS: List[str] = [
    "incident", "attack", "occurred", "reported", "stated", "group", "unknown",
    "sources", "claimed", "responsibility", "carried", "perpetrators", "targeted",
    "location", "area", "approximately", "authorities", "confirmed", "official"
]


def clean_summary_text(text: Any) -> str:
    """
    Cleans an individual summary narrative:
    removes excessive whitespace, special punctuation, and normalizes casing.
    """
    if not isinstance(text, str):
        return ""
    text = text.strip()
    if len(text) < MIN_SUMMARY_LEN:
        return ""
    # Remove HTML tags or escaped entities if present
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove bracketed source references common in GTD, e.g. [source: BBC]
    text = re.sub(r"\[.*?\]", " ", text)
    # Standardize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def prepare_text_corpus(df: pd.DataFrame, text_col: str = "summary") -> pd.DataFrame:
    """
    Filters and cleans incident records to only those with meaningful narrative summaries.
    Adds a 'clean_summary' column.
    """
    if text_col not in df.columns:
        raise ValueError(f"Required narrative column '{text_col}' not found in DataFrame.")

    subset = df.dropna(subset=[text_col]).copy()
    subset["clean_summary"] = subset[text_col].apply(clean_summary_text)
    subset = subset[subset["clean_summary"].str.len() >= MIN_SUMMARY_LEN].copy()
    return subset


def fit_nmf_topics(
    df: pd.DataFrame,
    text_col: str = "clean_summary",
    n_topics: int = 5,
    max_features: int = 1000,
    top_words_per_topic: int = 8,
    random_state: int = 42,
) -> Tuple[NMF, TfidfVectorizer, List[Dict[str, Any]], pd.DataFrame]:
    """
    Discovers latent tactical themes using TF-IDF and Non-Negative Matrix Factorization (NMF).

    Returns:
        nmf_model: Trained NMF model.
        vectorizer: Fitted TfidfVectorizer.
        topic_info: List of dicts with topic metadata (topic_id, top_words, label).
        enriched_df: DataFrame with 'dominant_topic' (int) and 'dominant_topic_label' (str).
    """
    if text_col not in df.columns:
        df = prepare_text_corpus(df, "summary" if "summary" in df.columns else text_col)

    if len(df) == 0:
        raise ValueError("Corpus is empty. Cannot fit NMF topic model.")

    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    combined_stopwords = list(ENGLISH_STOP_WORDS.union(set(GTD_TEXT_STOPWORDS)))

    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words=combined_stopwords,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.90,
    )
    tfidf_matrix = vectorizer.fit_transform(df[text_col])

    # Ensure n_components does not exceed matrix rank
    actual_topics = min(n_topics, tfidf_matrix.shape[1], tfidf_matrix.shape[0])
    if actual_topics < 1:
        actual_topics = 1

    nmf_model = NMF(
        n_components=actual_topics,
        random_state=random_state,
        init="nndsvda",
        max_iter=300,
    )
    topic_weights = nmf_model.fit_transform(tfidf_matrix)
    feature_names = vectorizer.get_feature_names_out()

    topic_info = []
    for topic_idx, component in enumerate(nmf_model.components_):
        top_feature_indices = component.argsort()[: -top_words_per_topic - 1 : -1]
        top_words = [feature_names[i] for i in top_feature_indices]
        label = f"Topic {topic_idx + 1}: {', '.join(top_words[:3]).title()}"
        topic_info.append({
            "topic_id": topic_idx,
            "top_words": top_words,
            "label": label,
        })

    enriched_df = df.copy()
    enriched_df["dominant_topic"] = topic_weights.argmax(axis=1)
    label_map = {t["topic_id"]: t["label"] for t in topic_info}
    enriched_df["dominant_topic_label"] = enriched_df["dominant_topic"].map(label_map)

    return nmf_model, vectorizer, topic_info, enriched_df


def get_topic_prevalence_over_time(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes annual distribution of dominant topics over time (1970-2017).
    """
    if "dominant_topic_label" not in enriched_df.columns or "iyear" not in enriched_df.columns:
        return pd.DataFrame()

    crosstab = pd.crosstab(
        enriched_df["iyear"],
        enriched_df["dominant_topic_label"],
        normalize="index"
    ) * 100.0
    return crosstab.reset_index()


def get_topic_prevalence_by_region(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes regional percentage distribution of dominant topics.
    """
    if "dominant_topic_label" not in enriched_df.columns or "region_txt" not in enriched_df.columns:
        return pd.DataFrame()

    crosstab = pd.crosstab(
        enriched_df["region_txt"],
        enriched_df["dominant_topic_label"],
        normalize="index"
    ) * 100.0
    return crosstab.reset_index()


def extract_named_entities(
    texts: List[str],
    max_docs: int = 500,
    top_n: int = 15,
) -> Dict[str, List[Tuple[str, int]]]:
    """
    Extracts named entities (GPE, ORG, PERSON) from narrative texts.
    Attempts spaCy extraction with 'en_core_web_sm'. If spaCy or the model
    is unavailable, falls back to deterministic rule-based pattern extraction.
    """
    # Sample down to max_docs for fast execution
    sample_texts = texts[:max_docs] if len(texts) > max_docs else texts

    gpe_counter: Counter = Counter()
    org_counter: Counter = Counter()
    person_counter: Counter = Counter()

    use_spacy = False
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "attribute_ruler", "lemmatizer"])
            use_spacy = True
            for doc in nlp.pipe(sample_texts, batch_size=50):
                for ent in doc.ents:
                    clean_ent = ent.text.strip()
                    if len(clean_ent) < 3:
                        continue
                    if ent.label_ == "GPE":
                        gpe_counter[clean_ent] += 1
                    elif ent.label_ == "ORG":
                        org_counter[clean_ent] += 1
                    elif ent.label_ == "PERSON":
                        person_counter[clean_ent] += 1
        except Exception:
            use_spacy = False
    except ImportError:
        use_spacy = False

    if not use_spacy:
        # High-precision heuristic fallback
        org_keywords = {
            "Army", "Front", "Brigade", "Forces", "Police", "Movement", "Party", "Militia",
            "Council", "Union", "Taliban", "Al-Qaida", "ISIS", "ISIL", "Boko Haram",
            "FARC", "PKK", "ETA", "IRA", "Hamas", "Hezbollah", "Rebels", "Government"
        }
        person_honorifics = {"General", "Colonel", "President", "Commander", "Minister", "Mayor", "Leader", "Officer"}

        for text in sample_texts:
            tokens = re.findall(r"\b[A-Z][a-zA-Z0-9\-]+\b", text)
            for i, tok in enumerate(tokens):
                if tok in org_keywords or (i > 0 and tokens[i-1] in ["The", "National", "Islamic", "Liberation"] and tok in org_keywords):
                    org_counter[tok] += 1
                elif tok in person_honorifics and i + 1 < len(tokens):
                    full_name = f"{tok} {tokens[i+1]}"
                    person_counter[full_name] += 1

            # Common geopolitical keywords or locations preceded by in/at/near
            loc_matches = re.findall(r"\b(?:in|near|outside|city of|province of)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)", text)
            for loc in loc_matches:
                if len(loc) >= 3 and loc not in org_keywords and loc not in person_honorifics:
                    gpe_counter[loc] += 1

    return {
        "GPE": gpe_counter.most_common(top_n),
        "ORG": org_counter.most_common(top_n),
        "PERSON": person_counter.most_common(top_n),
    }


def compute_dense_embeddings(
    texts: List[str],
    dim: int = 128,
    random_state: int = 42,
) -> Tuple[np.ndarray, Optional[Any], Optional[Any]]:
    """
    Computes dense semantic embeddings.
    Tries SentenceTransformers ('all-MiniLM-L6-v2') first; if unavailable,
    falls back to normalized TF-IDF + TruncatedSVD dense projection.
    """
    try:
        import os
        if os.environ.get("USE_TFIDF_EMBEDDINGS") == "1":
            raise RuntimeError("TF-IDF fallback requested via environment.")
        from sentence_transformers import SentenceTransformer
        # Attempt local cache first to avoid hanging if network is sandboxed
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        except Exception:
            # If not yet downloaded locally, immediately use high-fidelity TF-IDF fallback
            raise RuntimeError("SentenceTransformer weights not cached locally; using fast TF-IDF fallback.")
        embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return np.asarray(embeddings, dtype=np.float32), model, None
    except Exception as e:
        logger.info(f"SentenceTransformer unavailable ({e}), using TF-IDF + TruncatedSVD fallback.")
        min_df = 1 if len(texts) < 50 else 2
        vectorizer = TfidfVectorizer(max_features=2000, stop_words="english", min_df=min_df)
        tfidf = vectorizer.fit_transform(texts)
        n_comp = min(dim, tfidf.shape[1] - 1, tfidf.shape[0] - 1)
        if n_comp < 2:
            n_comp = max(1, min(tfidf.shape[1], tfidf.shape[0]))
        svd = TruncatedSVD(n_components=n_comp, random_state=random_state)
        dense = svd.fit_transform(tfidf)
        # L2-normalize
        norms = np.linalg.norm(dense, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        dense = dense / norms
        return dense.astype(np.float32), vectorizer, svd


def search_similar_incidents(
    query: Union[str, int],
    embeddings: np.ndarray,
    meta_df: pd.DataFrame,
    top_k: int = 10,
    model: Optional[Any] = None,
    vectorizer: Optional[Any] = None,
    svd: Optional[Any] = None,
) -> pd.DataFrame:
    """
    Searches for the most semantically similar historical incidents.
    Supports:
      - Integer index query: returns incidents most similar to a chosen historical event.
      - String narrative query: embeds freeform analyst text and retrieves nearest matches.

    Returns:
        DataFrame containing metadata of top_k matches, including similarity_score.
    """
    if len(embeddings) == 0 or len(meta_df) == 0:
        return pd.DataFrame()

    if isinstance(query, (int, np.integer)):
        if query < 0 or query >= len(embeddings):
            raise IndexError(f"Query index {query} out of bounds for corpus of size {len(embeddings)}.")
        query_vec = embeddings[query]
    elif isinstance(query, str):
        query = query.strip()
        if not query:
            return pd.DataFrame()
        if model is not None and hasattr(model, "encode"):
            query_vec = model.encode([query], normalize_embeddings=True)[0]
        elif vectorizer is not None and svd is not None:
            tfidf = vectorizer.transform([query])
            dense = svd.transform(tfidf)[0]
            norm = np.linalg.norm(dense)
            query_vec = dense / (norm if norm > 0 else 1.0)
        else:
            # Fallback zero vector
            query_vec = np.zeros(embeddings.shape[1], dtype=np.float32)
    else:
        raise TypeError("Query must be an integer index or a narrative string.")

    # Compute cosine similarity (embeddings are already unit-norm)
    scores = np.dot(embeddings, query_vec)
    # Clip scores to [-1.0, 1.0] to prevent floating point anomalies
    scores = np.clip(scores, -1.0, 1.0)

    # Sort descending
    top_indices = np.argsort(scores)[::-1]

    # Exclude self if query was an integer index
    if isinstance(query, (int, np.integer)):
        top_indices = [idx for idx in top_indices if idx != query]

    top_indices = top_indices[:top_k]

    results = meta_df.iloc[top_indices].copy()
    results["similarity_score"] = scores[top_indices].round(4)
    return results

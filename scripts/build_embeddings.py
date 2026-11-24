"""
Offline script to precompute topic models, entity metrics, and semantic narrative embeddings.
Saves:
  - artifacts/nmf_topic_model.joblib
  - artifacts/embeddings.npy
  - artifacts/embeddings_meta.parquet
  - artifacts/fallback_vectorizer.joblib (if SVD fallback is used)

Ensures the Streamlit dashboard loads lightweight precomputed artifacts instantly
without exceeding the 1 GB memory limit or running intensive encoders on each turn.
"""

import logging
import sys
from pathlib import Path

# Ensure root workspace directory is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
import numpy as np
import pandas as pd

from src.config import ARTIFACTS_DIR, PROCESSED_DATA_PATH
from src.data_loader import load_dataset
from src.text_mining import (
    compute_dense_embeddings,
    fit_nmf_topics,
    prepare_text_corpus,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_embeddings")


def main() -> None:
    logger.info("Initializing incident narrative text mining pipeline...")
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    if PROCESSED_DATA_PATH.exists():
        logger.info(f"Loading processed dataset from {PROCESSED_DATA_PATH}...")
        df = pd.read_parquet(PROCESSED_DATA_PATH)
    else:
        logger.info("Processed dataset not found, generating cleaned corpus via data_loader...")
        df = load_dataset()

    logger.info(f"Total raw incidents: {len(df):,}")

    # Prepare cleaned narrative corpus
    logger.info("Filtering and sanitizing incident summary narratives...")
    corpus_df = prepare_text_corpus(df, text_col="summary")
    logger.info(f"Valid narrative summaries retained: {len(corpus_df):,}")

    if len(corpus_df) == 0:
        logger.warning("No valid summaries found. Creating fallback synthetic narrative rows...")
        # Create minimal fallback if summaries are empty
        corpus_df = df.head(100).copy()
        corpus_df["clean_summary"] = (
            corpus_df["gname"].astype(str) + " carried out an attack in " +
            corpus_df["country_txt"].astype(str) + " targeting " +
            corpus_df["targtype1_txt"].astype(str) + " using " +
            corpus_df["weaptype1_txt"].astype(str)
        )

    # 1. Train and save NMF Topic Model
    logger.info("Fitting TF-IDF + NMF topic model (5 topics)...")
    nmf_model, tfidf_vec, topic_info, enriched_corpus = fit_nmf_topics(
        corpus_df,
        text_col="clean_summary",
        n_topics=5,
        max_features=1500,
        random_state=42,
    )

    topic_artifact_path = ARTIFACTS_DIR / "nmf_topic_model.joblib"
    joblib.dump(
        {
            "nmf_model": nmf_model,
            "vectorizer": tfidf_vec,
            "topic_info": topic_info,
        },
        topic_artifact_path,
    )
    logger.info(f"Saved topic model artifact to {topic_artifact_path}")

    # 2. Compute and save dense embeddings
    logger.info("Computing dense narrative semantic vectors...")
    texts = corpus_df["clean_summary"].tolist()
    embeddings, encoder, svd = compute_dense_embeddings(texts, dim=128, random_state=42)

    embeddings_path = ARTIFACTS_DIR / "embeddings.npy"
    np.save(embeddings_path, embeddings)
    logger.info(f"Saved {embeddings.shape[0]:,} embeddings of dimension {embeddings.shape[1]} to {embeddings_path}")

    if svd is not None and encoder is not None:
        fallback_path = ARTIFACTS_DIR / "fallback_vectorizer.joblib"
        joblib.dump({"vectorizer": encoder, "svd": svd}, fallback_path)
        logger.info(f"Saved SVD fallback vectorizer to {fallback_path}")

    # 3. Save metadata table corresponding exactly to embedding row indices
    meta_cols = [
        "iyear", "imonth", "iday", "country_txt", "region_txt", "provstate", "city",
        "attacktype1_txt", "targtype1_txt", "weaptype1_txt", "gname",
        "nkill", "nwound", "ncasualty", "clean_summary"
    ]
    meta_cols = [col for col in meta_cols if col in enriched_corpus.columns]
    meta_df = enriched_corpus[meta_cols].reset_index(drop=True)

    meta_path = ARTIFACTS_DIR / "embeddings_meta.parquet"
    meta_df.to_parquet(meta_path, index=False)
    logger.info(f"Saved embedding metadata ({len(meta_df):,} rows) to {meta_path}")

    logger.info("Phase 8 text mining precomputations completed successfully.")


if __name__ == "__main__":
    main()

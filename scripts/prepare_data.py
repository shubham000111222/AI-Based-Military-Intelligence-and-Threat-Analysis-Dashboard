"""
Data preparation script for the Global Terrorism Database.
Loads raw Kaggle GTD CSV, filters the 20 analytical columns, executes the cleaning pipeline,
and outputs an optimized Parquet dataset at data/processed/gtd_slim.parquet.
If raw data is absent, provides download guidance and generates high-fidelity synthetic data.
"""

import argparse
import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import (
    PROCESSED_DATA_PATH,
    RAW_DATA_PATH,
    RAW_ENCODING,
    RAW_LOW_MEMORY,
)
from src.data_loader import clean_data, generate_synthetic_gtd, load_raw_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("prepare_data")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare GTD slim Parquet dataset for the AI Threat Analysis Dashboard."
    )
    parser.add_argument(
        "--raw-path",
        type=Path,
        default=RAW_DATA_PATH,
        help="Path to raw GTD CSV file (default: data/raw/globalterrorismdb_0718dist.csv)",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=PROCESSED_DATA_PATH,
        help="Destination path for processed Parquet (default: data/processed/gtd_slim.parquet)",
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="Force generation of synthetic GTD dataset even if raw data exists.",
    )
    parser.add_argument(
        "--n-records",
        type=int,
        default=15000,
        help="Number of records to generate when creating synthetic dataset (default: 15,000).",
    )
    args = parser.parse_args()

    start_time = time.time()
    logger.info("Initializing GTD data preparation...")

    output_path = args.output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.synthetic or not args.raw_path.exists():
        if not args.synthetic:
            logger.warning("=" * 70)
            logger.warning("NOTICE: Raw GTD dataset not found at '%s'.", args.raw_path)
            logger.warning(
                "To use real START data, download 'globalterrorismdb_0718dist.csv' from Kaggle:"
            )
            logger.warning("https://www.kaggle.com/datasets/START-UMD/gtd")
            logger.warning("and place it at: %s", args.raw_path)
            logger.warning("Generating %d synthetic GTD records for development...", args.n_records)
            logger.warning("=" * 70)

        df_raw = generate_synthetic_gtd(n_records=args.n_records, seed=42)
        logger.info("Generated %d synthetic raw records.", len(df_raw))
    else:
        logger.info("Raw dataset located at '%s'. Loading with %s...", args.raw_path, RAW_ENCODING)
        df_raw = load_raw_data(
            filepath=args.raw_path,
            encoding=RAW_ENCODING,
            low_memory=RAW_LOW_MEMORY,
        )

    # Execute cleaning pipeline
    logger.info("Running GTD cleaning pipeline...")
    df_clean = clean_data(df_raw, is_raw=True, collapse_rare=True)

    # Save to Parquet
    logger.info("Writing cleaned dataset to Parquet: %s", output_path)
    df_clean.to_parquet(output_path, index=False, engine="pyarrow", compression="snappy")

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    elapsed = time.time() - start_time

    logger.info("SUCCESS: Parquet generated successfully in %.2f seconds.", elapsed)
    logger.info("Total rows: %d | Total columns: %d | File size: %.2f MB", len(df_clean), len(df_clean.columns), file_size_mb)
    logger.info("Columns saved: %s", list(df_clean.columns))


if __name__ == "__main__":
    main()

"""
run_pipeline.py
-----------------
Orchestrates the full ETL flow, in order:

    Raw CSV -> Extract -> Assess Quality -> Clean -> Validate -> Load -> Processed CSV

Run it with:
    python run_pipeline.py

If validation fails, the pipeline still saves the output but prints a clear
warning so you can inspect reports/data_quality/validation_report.json
before trusting the processed data.
"""

import sys
import time

from utils import get_logger
from extract import extract_all
from assess_quality import assess_all
from clean_data import clean_all
from validate import validate_all
from load import load_all_to_csv

logger = get_logger("pipeline")


def run_pipeline(load_to_db: bool = False) -> None:
    start = time.time()
    logger.info("=" * 60)
    logger.info("STARTING ETL PIPELINE")
    logger.info("=" * 60)

    # 1. Extract
    logger.info("STEP 1/5 — Extract")
    raw_datasets = extract_all()
    if not raw_datasets:
        logger.error("No datasets extracted. Check datasets/raw/. Aborting.")
        sys.exit(1)

    # 2. Assess Data Quality
    logger.info("STEP 2/5 — Assess Data Quality")
    assess_all(raw_datasets)

    # 3. Clean
    logger.info("STEP 3/5 — Cleaning")
    cleaned_datasets = clean_all(raw_datasets)

    # 4. Validate
    logger.info("STEP 4/5 — Validation")
    validation_report = validate_all(cleaned_datasets)
    if not validation_report["ok"]:
        logger.warning(
            f"Validation found {validation_report['issue_count']} issue(s) — "
            "see reports/data_quality/validation_report.json. Continuing anyway."
        )

    # 5. Load
    logger.info("STEP 5/5 — Load")
    load_all_to_csv(cleaned_datasets)

    if load_to_db:
        from load import load_to_postgres
        load_to_postgres(cleaned_datasets)

    elapsed = time.time() - start
    logger.info("=" * 60)
    logger.info(f"PIPELINE COMPLETE in {elapsed:.1f}s")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_pipeline(load_to_db=False)

"""
utils.py
--------
Shared helpers used by every module in the ETL pipeline:
- centralized path config (so paths aren't hardcoded everywhere)
- a consistent logger
- small IO helpers (save/load CSV, save JSON reports)

Keeping this in one place means if the folder structure ever changes,
you only update it here instead of in 5 different files.
"""

import logging
import json
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Project paths (all relative to the project root, one level up from etl/)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "datasets" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "datasets" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports" / "data_quality"

for _dir in (RAW_DIR, PROCESSED_DIR, REPORTS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def get_logger(name: str) -> logging.Logger:
    """Return a logger with consistent formatting across all modules."""
    logger = logging.getLogger(name)
    if not logger.handlers:  # avoid duplicate handlers on re-import
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------
def list_raw_csv_files(raw_dir: Path = RAW_DIR) -> list[Path]:
    """Return every CSV file found in the raw datasets folder."""
    return sorted(raw_dir.glob("*.csv"))


def dataset_name_from_path(path: Path) -> str:
    """
    Turn a filename like 'olist_customers_dataset.csv' into a short,
    readable key: 'customers'. Falls back to the stem if the pattern
    doesn't match (so it still works for non-Olist files later).
    """
    stem = path.stem
    stem = stem.replace("olist_", "").replace("_dataset", "")
    return stem


def save_json_report(data: dict, out_path: Path) -> None:
    """Save a dict as a pretty-printed JSON report."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def save_dataframe(df: pd.DataFrame, out_path: Path) -> None:
    """Save a DataFrame to CSV without the pandas index column."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

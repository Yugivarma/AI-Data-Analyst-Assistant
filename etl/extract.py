"""
Module 1: Extract
------------------
Reads every CSV file found in datasets/raw/ automatically — no need to
hardcode filenames. New CSVs dropped into raw/ get picked up on the next run.

Output: a dict of {dataset_name: DataFrame}, e.g.
    {
        "customers": <DataFrame>,
        "orders": <DataFrame>,
        ...
    }
"""

import pandas as pd

from utils import RAW_DIR, list_raw_csv_files, dataset_name_from_path, get_logger

logger = get_logger("extract")


def extract_all(raw_dir=RAW_DIR) -> dict[str, pd.DataFrame]:
    """
    Read all CSV files in raw_dir into a dict of DataFrames.

    Uses a couple of defensive read options because real-world CSVs
    (this Olist dataset included) sometimes have:
    - a UTF-8 BOM on the first column header
    - mixed dtypes in a column (pandas warns, not errors)
    """
    csv_files = list_raw_csv_files(raw_dir)

    if not csv_files:
        logger.warning(f"No CSV files found in {raw_dir}")
        return {}

    logger.info(f"Found {len(csv_files)} CSV file(s) in {raw_dir}")

    datasets: dict[str, pd.DataFrame] = {}
    for path in csv_files:
        name = dataset_name_from_path(path)
        try:
            df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
            datasets[name] = df
            logger.info(f"Loaded '{name}' <- {path.name} | shape={df.shape}")
        except Exception as e:
            logger.error(f"Failed to read {path.name}: {e}")

    return datasets


if __name__ == "__main__":
    data = extract_all()
    print(f"\nExtracted {len(data)} datasets:")
    for name, df in data.items():
        print(f"  - {name}: {df.shape[0]:,} rows x {df.shape[1]} cols")

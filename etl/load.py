"""
Module 5: Load
----------------
Saves the cleaned + validated DataFrames to datasets/processed/ as CSVs.
This is the final ETL output — the "single source of truth" that both
PostgreSQL and the AI Data Analyst Assistant backend will read from.

PostgreSQL loading is included but OFF by default (`load_to_postgres=False`
in run_pipeline). Turn it on once your database/ schema is ready and your
.env has valid DB credentials.
"""

import os

import pandas as pd

from utils import PROCESSED_DIR, get_logger, save_dataframe

logger = get_logger("load")

def load_all_to_csv(datasets: dict[str, pd.DataFrame]) -> None:
    """
    Save all cleaned datasets to datasets/processed/.
    Existing processed CSV files are overwritten.
    """

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for name, df in datasets.items():
        output_path = PROCESSED_DIR / f"{name}.csv"

        save_dataframe(df, output_path)

        logger.info(
            f"[CSV LOAD] {name}: saved {len(df):,} rows -> {output_path}"
        )

def load_to_postgres(
    datasets: dict[str, pd.DataFrame],
    if_exists: str = "append"
) -> None:
    """
    Load validated datasets into existing PostgreSQL tables.

    Tables are loaded in foreign-key dependency order.
    Database credentials are read from environment variables.
    """

    try:
        from sqlalchemy import create_engine
    except ImportError:
        logger.error(
            "sqlalchemy is not installed. "
            "Run: pip install sqlalchemy psycopg2-binary"
        )
        return

    from dotenv import load_dotenv

    load_dotenv()

    host = os.getenv("PG_HOST", "localhost")
    port = os.getenv("PG_PORT", "5432")
    db = os.getenv("PG_DB", "ai_data_analyst")
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD")

    if not password:
        raise ValueError(
            "PG_PASSWORD is not set. "
            "Add it to your .env file."
        )

    engine = create_engine(
        f"postgresql+psycopg2://"
        f"{user}:{password}@{host}:{port}/{db}"
    )

    load_order = [
        "customers",
        "products",
        "sellers",
        "product_category_name_translation",
        "orders",
        "order_items",
        "order_payments",
        "order_reviews",
        "geolocation",
    ]

    for table_name in load_order:

        if table_name not in datasets:
            logger.warning(
                f"Dataset '{table_name}' not found. Skipping."
            )
            continue

        df = datasets[table_name]

        logger.info(
            f"Loading '{table_name}' "
            f"({len(df):,} rows)..."
        )

        df.to_sql(
            table_name,
            engine,
            schema="analytics",
            if_exists=if_exists,
            index=False,
            chunksize=5000,
            method="multi"
        )

        logger.info(
            f"Loaded '{table_name}' successfully."
        )

    logger.info("PostgreSQL load complete.")
"""
AI Data Analyst Assistant
Phase 3.6.9 - PostgreSQL Database Loader

Loads validated processed CSV files into existing PostgreSQL tables.

Important:
- Does NOT recreate tables.
- Uses append mode.
- Loads tables in dependency order.
- Each table is handled independently.
- A failure in one table does not prevent independent tables
  from being attempted.
"""

import logging
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = PROJECT_ROOT / "datasets" / "processed"

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("database_loader")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def create_db_engine():

    host = os.getenv("PG_HOST", "localhost")
    port = os.getenv("PG_PORT", "5432")
    database = os.getenv("PG_DB", "ai_data_analyst")
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD")

    if not password:
        raise ValueError(
            "PG_PASSWORD is missing from .env"
        )

    connection_url = (
        f"postgresql+psycopg2://"
        f"{user}:{password}@{host}:{port}/{database}"
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True
    )


# ============================================================
# LOAD ORDER
# ============================================================

LOAD_ORDER = [
    "order_payments"
]


# ============================================================
# CSV VALIDATION
# ============================================================

def validate_csv(table_name, df):

    logger.info(
        "Validating %s...",
        table_name
    )

    if df.empty:

        raise ValueError(
            f"{table_name}.csv contains 0 rows"
        )

    logger.info(
    "%s contains %s rows and %s columns",
    table_name,
    f"{len(df):,}",
    len(df)
)


# ============================================================
# DATABASE ROW COUNT
# ============================================================

def get_database_count(engine, table_name):

    query = text(
        f"""
        SELECT COUNT(*)
        FROM analytics."{table_name}";
        """
    )

    with engine.connect() as connection:

        result = connection.execute(query)

        return result.scalar()


# ============================================================
# LOAD ONE TABLE
# ============================================================

def load_table(engine, table_name):

    csv_path = PROCESSED_DIR / f"{table_name}.csv"

    logger.info("=" * 70)
    logger.info("TABLE: %s", table_name)
    logger.info("=" * 70)

    if not csv_path.exists():

        raise FileNotFoundError(
            f"Missing file: {csv_path}"
        )

    logger.info(
        "Reading: %s",
        csv_path
    )

    df = pd.read_csv(csv_path)

    validate_csv(table_name, df)

    start_time = time.time()

    logger.info(
    "Loading %s rows into analytics.%s...",
    f"{len(df):,}",
    table_name
)

    df.to_sql(
        name=table_name,
        con=engine,
        schema="analytics",
        if_exists="append",
        index=False,
        chunksize=5000
    )

    elapsed = time.time() - start_time

    database_count = get_database_count(
        engine,
        table_name
    )

    logger.info(
        "Successfully loaded %s",
        table_name
    )

    logger.info(
        "CSV rows: %,d",
        len(df)
    )

    logger.info(
        "Database rows: %,d",
        database_count
    )

    logger.info(
        "Time: %.2f seconds",
        elapsed
    )

    return len(df), database_count


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info("=" * 70)
    logger.info("AI DATA ANALYST ASSISTANT")
    logger.info("POSTGRESQL DATA LOAD")
    logger.info("=" * 70)

    logger.info(
        "Processed directory: %s",
        PROCESSED_DIR
    )

    if not PROCESSED_DIR.exists():

        raise FileNotFoundError(
            f"Processed directory does not exist: {PROCESSED_DIR}"
        )

    engine = create_db_engine()

    # Test database connection
    with engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT current_database(), current_user;
                """
            )
        )

        database, user = result.fetchone()

        logger.info(
            "Connected to database: %s",
            database
        )

        logger.info(
            "Connected as user: %s",
            user
        )

    successful = []
    failed = []

    # --------------------------------------------------------
    # Load tables independently
    # --------------------------------------------------------

    for table_name in LOAD_ORDER:

        try:

            csv_rows, database_rows = load_table(
                engine,
                table_name
            )

            successful.append(
                (
                    table_name,
                    csv_rows,
                    database_rows
                )
            )

        except Exception as error:

            logger.error(
                "FAILED: %s",
                table_name
            )

            logger.error(
                "ERROR: %s",
                error
            )

            failed.append(
                (
                    table_name,
                    str(error)
                )
            )

            # Continue to next table
            continue

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    logger.info("")
    logger.info("=" * 70)
    logger.info("DATABASE LOAD SUMMARY")
    logger.info("=" * 70)

    logger.info("SUCCESSFUL TABLES:")

    for table_name, csv_rows, database_rows in successful:

        logger.info(
            "  %-40s CSV=%10,d DB=%10,d",
            table_name,
            csv_rows,
            database_rows
        )

    logger.info("")

    if failed:

        logger.info("FAILED TABLES:")

        for table_name, error in failed:

            logger.error(
                "  %-40s %s",
                table_name,
                error
            )

    else:

        logger.info(
            "ALL TABLES LOADED SUCCESSFULLY!"
        )

    logger.info("=" * 70)


if __name__ == "__main__":
    main()
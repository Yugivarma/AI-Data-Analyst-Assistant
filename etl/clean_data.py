"""
Module 3: Cleaning
-------------------
This module fixes ONLY the issues that Module 2 (assess_quality) actually
found in this dataset. Nothing here is speculative — every step below is
tied to a specific finding from the quality reports:

    geolocation
        - 261,831 full duplicate rows                -> drop duplicates
        - 68 rows with lat/lng outside Brazil's bbox   -> drop (bad geocoding)

    orders
        - date columns stored as text                  -> parse to datetime
        - order_approved_at / delivered_carrier_date /
          delivered_customer_date have real nulls       -> KEEP as NaT
          (these are legitimate: e.g. a canceled order was never delivered,
          so "delivered date" being empty is correct, not dirty data)

    order_reviews
        - date columns stored as text                   -> parse to datetime
        - review_comment_title (88%) / message (59%)
          missing                                        -> KEEP as null
          (most customers just don't leave a written comment; filling
          these with a placeholder would fabricate data, not clean it)

    products
        - product_category_name missing (610 rows)      -> fill "unknown"
        - product_name_lenght / description_lenght /
          photos_qty missing (same 610 rows)             -> fill 0
        - product_weight_g/length/height/width missing
          (only 2 rows)                                   -> impute with
          column median, NOT drop. These 2 products are still referenced
          by 18 rows in order_items — dropping them would silently break
          referential integrity downstream. Validation (Module 4) is what
          caught this: an early version dropped the rows and validate.py
          flagged 18 orphaned order_items.product_id values. Median
          imputation keeps every table's foreign keys intact.

    all datasets
        - strip leading/trailing whitespace on text columns (defensive;
          none was found in this data, but cheap insurance against the
          next CSV export that does have it)

Each cleaning function returns a NEW DataFrame and logs what it changed,
so the before/after is always visible when you run the pipeline.
"""

import pandas as pd

from utils import get_logger

logger = get_logger("clean_data")

# Rough bounding box for Brazil (used to catch clearly wrong geocoding)
BRAZIL_LAT_RANGE = (-34, 6)
BRAZIL_LNG_RANGE = (-74, -34)

DATE_LIKE_SUFFIXES = ("_date", "_timestamp", "_at")


def _strip_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Trim leading/trailing whitespace on every text (object/string) column."""
    df = df.copy()
    text_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in text_cols:
        df[col] = df[col].str.strip()
    return df


def _parse_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert any column that looks like a date/timestamp to real datetime dtype."""
    df = df.copy()
    for col in df.columns:
        if col.endswith(DATE_LIKE_SUFFIXES):
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_whitespace(df)
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"[customers] dropped {before - len(df)} full duplicate rows")
    return df


def clean_geolocation(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_whitespace(df)

    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"[geolocation] dropped {before - len(df):,} full duplicate rows")

    before = len(df)
    valid_lat = df["geolocation_lat"].between(*BRAZIL_LAT_RANGE)
    valid_lng = df["geolocation_lng"].between(*BRAZIL_LNG_RANGE)
    df = df[valid_lat & valid_lng]
    logger.info(f"[geolocation] dropped {before - len(df)} rows with lat/lng outside Brazil")

    return df.reset_index(drop=True)


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_whitespace(df)
    df = _parse_date_columns(df)
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"[orders] dropped {before - len(df)} full duplicate rows")
    logger.info(
        "[orders] kept nulls in order_approved_at / delivered_carrier_date / "
        "delivered_customer_date as-is (legitimate for undelivered/canceled orders)"
    )
    return df


def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_whitespace(df)
    df = _parse_date_columns(df)
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"[order_items] dropped {before - len(df)} full duplicate rows")
    return df


def clean_order_payments(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_whitespace(df)

    # Remove exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    logger.info(
        f"[order_payments] dropped {before - len(df):,} full duplicate rows"
    )

    # payment_installments must be greater than 0.
    # Quality assessment found 2 records with value 0.
    # Treat 0 as invalid and impute using the median of valid values.
    invalid_mask = df["payment_installments"] <= 0
    n_invalid = int(invalid_mask.sum())

    if n_invalid:
        median_installments = df.loc[
            df["payment_installments"] > 0,
            "payment_installments"
        ].median()

        df.loc[invalid_mask, "payment_installments"] = round(
            median_installments
        )

        logger.info(
            f"[order_payments] imputed {n_invalid:,} invalid "
            f"payment_installments values with median "
            f"({round(median_installments)})"
        )

    return df.reset_index(drop=True)


def clean_order_reviews(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_whitespace(df)
    df = _parse_date_columns(df)
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"[order_reviews] dropped {before - len(df)} full duplicate rows")
    logger.info(
        "[order_reviews] kept nulls in review_comment_title/message as-is "
        "(most customers leave a score without a written comment)"
    )
    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_whitespace(df)

    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"[products] dropped {before - len(df)} full duplicate rows")

    # 610 rows missing category + the 3 related metadata columns together
    df["product_category_name"] = df["product_category_name"].fillna("unknown")
    for col in ["product_name_lenght", "product_description_lenght", "product_photos_qty"]:
        n_filled = int(df[col].isna().sum())
        df[col] = df[col].fillna(0)
        if n_filled:
            logger.info(f"[products] filled {n_filled} missing '{col}' values with 0")

    # Only 2 rows missing physical dimensions. Dropping them looked safe in
    # isolation, but validation showed those product_ids are still used by
    # 18 rows in order_items -> dropping would orphan foreign keys there.
    # Median imputation keeps the row (and the FK relationship) intact.
    dimension_cols = ["product_weight_g", "product_length_cm",
                       "product_height_cm", "product_width_cm"]
    for col in dimension_cols:
        n_missing = int(df[col].isna().sum())
        if n_missing:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            logger.info(f"[products] imputed {n_missing} missing '{col}' with median ({median_val})")

    return df.reset_index(drop=True)


def clean_sellers(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_whitespace(df)
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"[sellers] dropped {before - len(df)} full duplicate rows")
    return df


def clean_category_translation(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_whitespace(df)
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"[product_category_name_translation] dropped {before - len(df)} duplicate rows")
    return df


# Maps dataset name -> cleaning function. If a new CSV shows up that isn't
# in this map, it falls back to a generic clean (strip + dedupe) below.
CLEANERS = {
    "customers": clean_customers,
    "geolocation": clean_geolocation,
    "orders": clean_orders,
    "order_items": clean_order_items,
    "order_payments": clean_order_payments,
    "order_reviews": clean_order_reviews,
    "products": clean_products,
    "sellers": clean_sellers,
    "product_category_name_translation": clean_category_translation,
}


def clean_all(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Apply the appropriate cleaning function to every dataset."""
    cleaned = {}
    for name, df in datasets.items():
        cleaner = CLEANERS.get(name)
        if cleaner is None:
            logger.warning(f"No specific cleaner for '{name}', applying generic clean")
            cleaner = lambda d: d.drop_duplicates().pipe(_strip_whitespace)
        cleaned[name] = cleaner(df)
    return cleaned


if __name__ == "__main__":
    from extract import extract_all

    raw = extract_all()
    cleaned = clean_all(raw)

    print("\nCleaning Summary (rows before -> after)")
    print("=" * 50)
    for name in raw:
        print(f"{name:15s} | {raw[name].shape[0]:>9,} -> {cleaned[name].shape[0]:>9,}")

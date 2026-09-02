"""
Module 4: Validation
----------------------
Runs a checklist against the CLEANED data to confirm cleaning actually
worked, before anything gets saved or loaded into PostgreSQL. This is the
pipeline's safety net — if validation fails, we want to know now, not
after bad data is sitting in the database.

Checks performed per dataset:
    1. Primary key columns have no nulls and no duplicates
    2. Expected dtypes (date columns are real datetime, not text)
    3. Value ranges are within business-valid bounds
    4. Referential integrity — foreign keys actually exist in the parent table
       (e.g. every order_items.order_id must exist in orders.order_id)

Results are collected into a report and saved to
reports/data_quality/validation_report.json. Any FAILED check is logged
loudly; the pipeline can decide whether to halt or continue based on
`ok` in the returned report.
"""

import pandas as pd

from utils import REPORTS_DIR, get_logger, save_json_report

logger = get_logger("validate")

# Primary key column per dataset (used for null + uniqueness checks)
PRIMARY_KEYS = {
    "customers": "customer_id",
    "orders": "order_id",
    "products": "product_id",
    "sellers": "seller_id",
}

# Foreign key relationships: (child_dataset, child_column) -> (parent_dataset, parent_column)
FOREIGN_KEYS = [
    (("orders", "customer_id"), ("customers", "customer_id")),
    (("order_items", "order_id"), ("orders", "order_id")),
    (("order_items", "product_id"), ("products", "product_id")),
    (("order_items", "seller_id"), ("sellers", "seller_id")),
    (("order_payments", "order_id"), ("orders", "order_id")),
    (("order_reviews", "order_id"), ("orders", "order_id")),
]

# Value-range rules: dataset -> {column: (min, max)} inclusive
RANGE_RULES = {
    "order_reviews": {"review_score": (1, 5)},
    "order_items": {"price": (0.01, None), "freight_value": (0, None)},
    "geolocation": {"geolocation_lat": (-34, 6), "geolocation_lng": (-74, -34)},
}

DATE_COLUMNS = {
    "orders": ["order_purchase_timestamp", "order_approved_at",
               "order_delivered_carrier_date", "order_delivered_customer_date",
               "order_estimated_delivery_date"],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"],
}


def _check_primary_key(name: str, df: pd.DataFrame, issues: list) -> None:
    pk = PRIMARY_KEYS.get(name)
    if pk is None or pk not in df.columns:
        return
    nulls = int(df[pk].isna().sum())
    dupes = int(df[pk].duplicated().sum())
    if nulls:
        issues.append(f"[{name}] {nulls} null value(s) in primary key '{pk}'")
    if dupes:
        issues.append(f"[{name}] {dupes} duplicate value(s) in primary key '{pk}'")


def _check_date_types(name: str, df: pd.DataFrame, issues: list) -> None:
    for col in DATE_COLUMNS.get(name, []):
        if col not in df.columns:
            continue
        if not pd.api.types.is_datetime64_any_dtype(df[col]):
            issues.append(f"[{name}] column '{col}' is not a datetime dtype")


def _check_ranges(name: str, df: pd.DataFrame, issues: list) -> None:
    for col, (lo, hi) in RANGE_RULES.get(name, {}).items():
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if lo is not None and (series < lo).any():
            n = int((series < lo).sum())
            issues.append(f"[{name}] {n} value(s) in '{col}' below minimum {lo}")
        if hi is not None and (series > hi).any():
            n = int((series > hi).sum())
            issues.append(f"[{name}] {n} value(s) in '{col}' above maximum {hi}")


def _check_foreign_keys(datasets: dict[str, pd.DataFrame], issues: list) -> None:
    for (child_ds, child_col), (parent_ds, parent_col) in FOREIGN_KEYS:
        if child_ds not in datasets or parent_ds not in datasets:
            continue
        child_df, parent_df = datasets[child_ds], datasets[parent_ds]
        if child_col not in child_df.columns or parent_col not in parent_df.columns:
            continue
        orphaned = ~child_df[child_col].isin(parent_df[parent_col])
        n_orphaned = int(orphaned.sum())
        if n_orphaned:
            issues.append(
                f"[{child_ds}] {n_orphaned} row(s) with '{child_col}' not found "
                f"in {parent_ds}.{parent_col}"
            )


def validate_all(datasets: dict[str, pd.DataFrame], reports_dir=REPORTS_DIR) -> dict:
    """
    Run every validation check across all cleaned datasets.
    Returns a report dict: {"ok": bool, "issues": [...], "checked": [...]}
    """
    issues: list[str] = []

    for name, df in datasets.items():
        _check_primary_key(name, df, issues)
        _check_date_types(name, df, issues)
        _check_ranges(name, df, issues)

    _check_foreign_keys(datasets, issues)

    report = {
        "ok": len(issues) == 0,
        "datasets_checked": list(datasets.keys()),
        "issue_count": len(issues),
        "issues": issues,
    }
    save_json_report(report, reports_dir / "validation_report.json")

    if report["ok"]:
        logger.info("Validation PASSED — no issues found across all datasets")
    else:
        logger.warning(f"Validation found {len(issues)} issue(s):")
        for issue in issues:
            logger.warning(f"  - {issue}")

    return report


if __name__ == "__main__":
    from extract import extract_all
    from clean_data import clean_all

    raw = extract_all()
    cleaned = clean_all(raw)
    report = validate_all(cleaned)

    print(f"\nValidation {'PASSED' if report['ok'] else 'FAILED'} "
          f"({report['issue_count']} issue(s))")

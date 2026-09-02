"""
Module 2: Assess Data Quality
------------------------------
For every extracted dataset, generate a data quality report covering:
    1. Missing values      (count + % per column)
    2. Duplicate rows       (full-row duplicates)
    3. Data types            (as pandas inferred them)
    4. Invalid values        (negative prices, out-of-range scores, bad dates, etc.)
    5. Unique values          (cardinality per column, useful for spotting
                               categorical columns / potential ID columns)

Each dataset gets its own JSON report saved to reports/data_quality/,
plus one combined summary report across all datasets. These reports are
what the Cleaning module (Module 3) reads to decide what actually needs
fixing — we don't clean blindly, we clean based on evidence.
"""

import pandas as pd

from utils import REPORTS_DIR, get_logger, save_json_report

logger = get_logger("assess_quality")

# ---------------------------------------------------------------------------
# Dataset-specific "should never happen" rules.
# Keys are dataset names (as produced by extract.dataset_name_from_path).
# Each rule is a short human-readable description + a callable that
# returns a boolean Series (True = invalid row).
# This is intentionally small and explicit — add more rules as you learn
# more about the data, rather than trying to guess everything up front.
# ---------------------------------------------------------------------------
INVALID_VALUE_RULES = {
    "order_items": {
        "negative_or_zero_price": lambda df: df["price"] <= 0,
        "negative_freight_value": lambda df: df["freight_value"] < 0,
    },
    "order_payments": {
        "negative_payment_value": lambda df: df["payment_value"] < 0,
        "non_positive_installments": lambda df: df["payment_installments"] < 0,
    },
    "order_reviews": {
        "review_score_out_of_range": lambda df: ~df["review_score"].between(1, 5),
    },
    "products": {
        "negative_weight": lambda df: df["product_weight_g"] < 0,
        "negative_dimensions": lambda df: (
            (df["product_length_cm"] < 0)
            | (df["product_height_cm"] < 0)
            | (df["product_width_cm"] < 0)
        ),
    },
    "geolocation": {
        "lat_out_of_brazil_range": lambda df: ~df["geolocation_lat"].between(-34, 6),
        "lng_out_of_brazil_range": lambda df: ~df["geolocation_lng"].between(-74, -34),
    },
    "orders": {
        "delivered_before_purchase": lambda df: (
            pd.to_datetime(df["order_delivered_customer_date"], errors="coerce")
            < pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
        ),
    },
}

# Columns that look like dates by name but are stored as text in the raw CSV.
# Used to check how many values fail to parse as real dates.
DATE_LIKE_SUFFIXES = ("_date", "_timestamp", "_at")


def _missing_values(df: pd.DataFrame) -> dict:
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    return {
        col: {"missing_count": int(missing_count[col]), "missing_pct": float(missing_pct[col])}
        for col in df.columns
        if missing_count[col] > 0
    }


def _duplicate_rows(df: pd.DataFrame) -> dict:
    full_dupes = int(df.duplicated().sum())
    return {
        "full_duplicate_rows": full_dupes,
        "full_duplicate_pct": round(full_dupes / len(df) * 100, 2) if len(df) else 0,
    }


def _data_types(df: pd.DataFrame) -> dict:
    return {col: str(dtype) for col, dtype in df.dtypes.items()}


def _invalid_dates(df: pd.DataFrame) -> dict:
    """Check any column that looks like a date column for unparseable values."""
    results = {}
    for col in df.columns:
        if col.endswith(DATE_LIKE_SUFFIXES):
            parsed = pd.to_datetime(df[col], errors="coerce")
            bad = int(parsed.isna().sum() - df[col].isna().sum())  # newly-NaT after parsing
            if bad > 0:
                results[col] = {"unparseable_dates": bad}
    return results


def _invalid_values(dataset_name: str, df: pd.DataFrame) -> dict:
    """Apply dataset-specific business rules (if any exist for this dataset)."""
    results = {}
    rules = INVALID_VALUE_RULES.get(dataset_name, {})
    for rule_name, rule_fn in rules.items():
        try:
            mask = rule_fn(df)
            bad_count = int(mask.sum())
            if bad_count > 0:
                results[rule_name] = bad_count
        except KeyError as e:
            logger.warning(f"[{dataset_name}] skipped rule '{rule_name}': missing column {e}")
    date_issues = _invalid_dates(df)
    if date_issues:
        results["unparseable_dates_by_column"] = date_issues
    return results


def _unique_values(df: pd.DataFrame, max_unique_to_list: int = 15) -> dict:
    """
    Report cardinality per column. For low-cardinality columns (likely
    categorical, e.g. order_status, payment_type) also list the values —
    handy for spotting typos/inconsistent casing.
    """
    results = {}
    for col in df.columns:
        n_unique = int(df[col].nunique(dropna=True))
        entry = {"unique_count": n_unique}
        if n_unique <= max_unique_to_list:
            entry["values"] = sorted(map(str, df[col].dropna().unique().tolist()))
        results[col] = entry
    return results


def assess_dataset(name: str, df: pd.DataFrame) -> dict:
    """Run all quality checks on a single dataset and return a report dict."""
    logger.info(f"Assessing '{name}' ({df.shape[0]:,} rows x {df.shape[1]} cols)")
    report = {
        "dataset": name,
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "missing_values": _missing_values(df),
        "duplicates": _duplicate_rows(df),
        "data_types": _data_types(df),
        "invalid_values": _invalid_values(name, df),
        "unique_values": _unique_values(df),
    }
    return report


def assess_all(datasets: dict[str, pd.DataFrame], reports_dir=REPORTS_DIR) -> dict[str, dict]:
    """Assess every dataset, save one JSON report per dataset + a combined summary."""
    all_reports = {}
    for name, df in datasets.items():
        report = assess_dataset(name, df)
        all_reports[name] = report
        save_json_report(report, reports_dir / f"{name}_quality_report.json")

    summary = _build_summary(all_reports)
    save_json_report(summary, reports_dir / "_summary_report.json")
    logger.info(f"Saved {len(all_reports)} dataset reports + summary to {reports_dir}")
    return all_reports


def _build_summary(all_reports: dict[str, dict]) -> dict:
    """A compact, top-level view: one row per dataset, key stats only."""
    summary = {}
    for name, report in all_reports.items():
        summary[name] = {
            "rows": report["shape"]["rows"],
            "columns": report["shape"]["columns"],
            "columns_with_missing_values": len(report["missing_values"]),
            "full_duplicate_rows": report["duplicates"]["full_duplicate_rows"],
            "invalid_value_flags": {k: v for k, v in report["invalid_values"].items()
                                     if k != "unparseable_dates_by_column"},
        }
    return summary


if __name__ == "__main__":
    from extract import extract_all

    data = extract_all()
    reports = assess_all(data)

    print("\nData Quality Summary")
    print("=" * 60)
    for name, report in reports.items():
        d = report["duplicates"]
        print(f"{name:15s} | rows={report['shape']['rows']:>7,} | "
              f"missing_cols={len(report['missing_values']):>2} | "
              f"dup_rows={d['full_duplicate_rows']:>5} | "
              f"invalid_flags={len(report['invalid_values'])}")

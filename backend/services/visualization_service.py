from decimal import Decimal


def detect_visualization_type(question: str, results: list[dict]) -> str:
    """
    Determine the most appropriate visualization type
    based on the user's question and query results.
    """

    question_lower = question.lower()

    if not results:
        return "table"

    time_keywords = [
        "over time",
        "monthly",
        "month",
        "yearly",
        "year",
        "trend",
        "growth",
        "weekly",
        "daily"
    ]

    if any(keyword in question_lower for keyword in time_keywords):
        return "line"

    ranking_keywords = [
        "top",
        "bottom",
        "highest",
        "lowest",
        "best",
        "worst",
        "compare",
        "comparison"
    ]

    if any(keyword in question_lower for keyword in ranking_keywords):
        return "bar"

    composition_keywords = [
        "share",
        "percentage",
        "percent",
        "proportion",
        "distribution",
        "breakdown"
    ]

    if any(keyword in question_lower for keyword in composition_keywords):
        return "pie"

    return "table"


def prepare_visualization_data(
    visualization_type: str,
    results: list[dict]
) -> dict:
    """
    Convert database results into a standardized
    visualization configuration.
    """

    if not results:
        return {
            "type": "table",
            "data": []
        }

    return {
        "type": visualization_type,
        "data": results
    }


def build_chart_config(
    visualization_type: str,
    results: list[dict]
) -> dict:
    """
    Build a chart configuration from SQL results.
    """

    if not results:
        return {
            "type": "table",
            "x_key": None,
            "y_key": None,
            "data": []
        }

    columns = list(results[0].keys())

    numeric_columns = []

    for column in columns:
        value = results[0].get(column)

        if isinstance(value, (int, float, Decimal)):
            numeric_columns.append(column)

        elif isinstance(value, str):
            try:
                float(value)
                numeric_columns.append(column)
            except ValueError:
                pass

    if not numeric_columns:
        return {
            "type": "table",
            "x_key": None,
            "y_key": None,
            "data": results
        }

    dimension_columns = [
        column
        for column in columns
        if column not in numeric_columns
    ]

    x_key = dimension_columns[0] if dimension_columns else None
    y_key = numeric_columns[0]

    return {
        "type": visualization_type,
        "x_key": x_key,
        "y_key": y_key,
        "data": results
    }

import re


FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "MERGE",
    "CALL",
    "EXEC",
    "EXECUTE",
    "COPY",
}

ALLOWED_SCHEMAS = {"analytics"}

FORBIDDEN_SCHEMAS = {
    "pg_catalog",
    "information_schema",
    "pg_toast",
}

FORBIDDEN_FUNCTIONS = {
    "pg_sleep",
    "pg_read_file",
    "pg_ls_dir",
    "pg_stat_file",
}


def validate_sql(query: str) -> str:
    """
    Validate AI-generated SQL before execution.

    Only read-only SELECT queries against the analytics schema
    are allowed.
    """

    if not query or not query.strip():
        raise ValueError("SQL query cannot be empty.")

    query = query.strip()

    # Remove one optional trailing semicolon.
    if query.endswith(";"):
        query = query[:-1].strip()

    # Multiple SQL statements are not allowed.
    if ";" in query:
        raise ValueError("Multiple SQL statements are not allowed.")

    # SQL comments are not allowed.
    if "--" in query:
        raise ValueError("SQL comments are not allowed.")

    if "/*" in query or "*/" in query:
        raise ValueError("SQL comments are not allowed.")

    # Only SELECT statements are allowed.
    if not re.match(r"^SELECT\b", query, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")

    # Block destructive or administrative SQL keywords.
    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{keyword}\b"

        if re.search(pattern, query, re.IGNORECASE):
            raise ValueError(
                f"Forbidden SQL keyword detected: {keyword}"
            )

    # Block access to PostgreSQL/system schemas.
    for schema in FORBIDDEN_SCHEMAS:
        pattern = rf"\b{re.escape(schema)}\s*\."

        if re.search(pattern, query, re.IGNORECASE):
            raise ValueError(
                f"Access to schema '{schema}' is not allowed."
            )

    # Inspect explicitly qualified identifiers.
    schema_references = re.findall(
        r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\.",
        query
    )

    for schema in schema_references:
        schema_lower = schema.lower()

        if schema_lower in FORBIDDEN_SCHEMAS:
            raise ValueError(
                f"Access to schema '{schema}' is not allowed."
            )

        if schema_lower not in ALLOWED_SCHEMAS:
            raise ValueError(
                f"Access to schema '{schema}' is not allowed."
            )

    # Block dangerous PostgreSQL functions.
    for function in FORBIDDEN_FUNCTIONS:
        pattern = rf"\b{re.escape(function)}\s*\("

        if re.search(pattern, query, re.IGNORECASE):
            raise ValueError(
                f"Forbidden SQL function detected: {function}"
            )

    return query
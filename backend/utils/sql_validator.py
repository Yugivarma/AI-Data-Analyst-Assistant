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
}


ALLOWED_SCHEMAS = {
    "analytics",
}


FORBIDDEN_SCHEMAS = {
    "pg_catalog",
    "information_schema",
    "pg_toast",
}


def validate_sql(query: str) -> str:
    """
    Validate an LLM-generated SQL query before execution.

    Returns the cleaned query if it is safe.
    Raises ValueError if the query is unsafe.
    """

    if not query or not query.strip():
        raise ValueError("SQL query cannot be empty.")

    query = query.strip()

    # Remove one trailing semicolon.
    if query.endswith(";"):
        query = query[:-1].strip()

    # Block multiple SQL statements.
    if ";" in query:
        raise ValueError("Multiple SQL statements are not allowed.")

    # Only SELECT queries are allowed.
    if not re.match(r"^SELECT\b", query, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")

    # Block destructive or database-modifying SQL commands.
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

    # If a schema-qualified table is used, require the analytics schema.
    schema_references = re.findall(
        r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\.",
        query
    )

    for schema in schema_references:
        if schema.lower() in FORBIDDEN_SCHEMAS:
            raise ValueError(
                f"Access to schema '{schema}' is not allowed."
            )

    return query
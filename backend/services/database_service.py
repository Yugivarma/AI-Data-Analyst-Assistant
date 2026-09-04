from sqlalchemy import text
from sqlalchemy.orm import Session


MAX_ROWS = 500
QUERY_TIMEOUT_MS = 10000


def execute_query(db: Session, query: str):
    """
    Execute a read-only SQL query safely.

    Limits returned rows and applies a PostgreSQL statement timeout
    to prevent expensive queries from running indefinitely.
    """

    # Limit the number of returned rows when the query does not
    # already contain a LIMIT clause.
    if " limit " not in query.lower():
        query = f"""
        SELECT *
        FROM (
            {query}
        ) AS limited_query
        LIMIT {MAX_ROWS}
        """

    # Set a 10-second timeout for this database session.
    db.execute(
        text("SET LOCAL statement_timeout = :timeout"),
        {"timeout": QUERY_TIMEOUT_MS}
    )

    result = db.execute(text(query))

    rows = result.mappings().fetchmany(MAX_ROWS)

    return [dict(row) for row in rows]
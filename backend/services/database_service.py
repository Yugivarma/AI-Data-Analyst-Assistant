from sqlalchemy import text
from sqlalchemy.orm import Session


def execute_query(db: Session, query: str):
    """
    Execute a SQL query and return the results as dictionaries.
    """

    result = db.execute(text(query))

    rows = result.mappings().all()

    return [dict(row) for row in rows]
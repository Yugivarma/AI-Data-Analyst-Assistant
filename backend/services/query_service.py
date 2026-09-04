from sqlalchemy.orm import Session

from backend.llm.client import generate_sql, generate_insight
from backend.utils.sql_validator import validate_sql
from backend.services.database_service import execute_query
# pyrefly: ignore [missing-import]
from backend.services.visualization_service import (detect_visualization_type,build_chart_config)


def answer_question(db: Session, question: str):
    """
    Convert a natural-language question into SQL,
    validate the SQL, execute it, and generate
    a business insight from the results.
    """

    # Step 1: Generate SQL using Gemini
    generated_sql = generate_sql(question)

    # Step 2: Validate the generated SQL
    safe_sql = validate_sql(generated_sql)

    # Step 3: Execute the validated SQL
    results = execute_query(db, safe_sql)
    
    # Step 4: Determine visualization
    visualization_type = detect_visualization_type(
        question,
        results
    )

    visualization = build_chart_config(
        visualization_type,
        results
    )

    # Step 5: Generate a business insight
    insight = generate_insight(
        question=question,
        sql=safe_sql,
        results=results
    )

    return {
        "question": question,
        "sql": safe_sql,
        "results": results,
        "insight": insight,
        "visualization": visualization
    }
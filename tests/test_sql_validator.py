import pytest

from backend.utils.sql_validator import validate_sql


def test_valid_select_query():
    query = """
        SELECT category, total_revenue
        FROM analytics.category_performance
        ORDER BY total_revenue DESC
        LIMIT 5;
    """

    result = validate_sql(query)

    assert result.startswith("SELECT")
    assert result.endswith("LIMIT 5")


@pytest.mark.parametrize(
    "query",
    [
        "DROP TABLE analytics.orders",
        "DELETE FROM analytics.orders",
        "UPDATE analytics.orders SET order_status = 'x'",
        "INSERT INTO analytics.orders VALUES ('test')",
        "ALTER TABLE analytics.orders ADD COLUMN test TEXT",
        "TRUNCATE analytics.orders",
    ],
)
def test_dangerous_queries_are_rejected(query):
    with pytest.raises(ValueError):
        validate_sql(query)


def test_multiple_statements_are_rejected():
    query = """
        SELECT *
        FROM analytics.orders;
        DROP TABLE analytics.orders
    """

    with pytest.raises(ValueError):
        validate_sql(query)


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM pg_catalog.pg_tables",
        "SELECT * FROM information_schema.tables",
        "SELECT * FROM pg_toast.some_table",
    ],
)
def test_system_schemas_are_rejected(query):
    with pytest.raises(ValueError):
        validate_sql(query)


def test_sql_comments_are_rejected():
    queries = [
        "SELECT * FROM analytics.orders -- comment",
        "SELECT * FROM analytics.orders /* comment */",
    ]

    for query in queries:
        with pytest.raises(ValueError):
            validate_sql(query)


def test_dangerous_postgresql_functions_are_rejected():
    queries = [
        "SELECT pg_sleep(10)",
        "SELECT pg_read_file('/etc/passwd')",
        "SELECT pg_ls_dir('.')",
        "SELECT pg_stat_file('test.txt')",
    ]

    for query in queries:
        with pytest.raises(ValueError):
            validate_sql(query)


def test_empty_query_is_rejected():
    with pytest.raises(ValueError):
        validate_sql("")


def test_non_select_query_is_rejected():
    with pytest.raises(ValueError):
        validate_sql("UPDATE analytics.orders SET order_status = 'x'")
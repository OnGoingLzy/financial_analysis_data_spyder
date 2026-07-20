import sqlite3

from financial_schema import ensure_normalized_schema


def test_schema_creation_is_idempotent():
    connection = sqlite3.connect(":memory:")
    ensure_normalized_schema(connection)
    ensure_normalized_schema(connection)
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"companies", "income_statements", "balance_sheets", "import_batches", "data_quality_issues"} <= tables
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 1


def test_amount_and_ratio_columns_have_stable_types():
    connection = sqlite3.connect(":memory:")
    ensure_normalized_schema(connection)
    income_types = {row[1]: row[2] for row in connection.execute("PRAGMA table_info(income_statements)")}
    assert income_types["net_profit"] == "INTEGER"
    assert income_types["gross_profit_margin"] == "REAL"

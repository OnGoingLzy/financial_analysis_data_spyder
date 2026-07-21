import sqlite3
from datetime import datetime, timedelta

from financial_schema import beijing_now, ensure_normalized_schema, to_beijing_timestamp


def test_schema_creation_is_idempotent():
    connection = sqlite3.connect(":memory:")
    ensure_normalized_schema(connection)
    ensure_normalized_schema(connection)
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"companies", "income_statements", "balance_sheets", "cash_flow_statements", "import_batches", "data_quality_issues"} <= tables
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 2


def test_amount_and_ratio_columns_have_stable_types():
    connection = sqlite3.connect(":memory:")
    ensure_normalized_schema(connection)
    income_types = {row[1]: row[2] for row in connection.execute("PRAGMA table_info(income_statements)")}
    assert income_types["net_profit"] == "INTEGER"
    assert income_types["gross_profit_margin"] == "REAL"


def test_standard_timestamps_use_beijing_timezone():
    assert datetime.fromisoformat(beijing_now()).utcoffset() == timedelta(hours=8)
    assert to_beijing_timestamp("2026-07-20T05:41:17+00:00") == "2026-07-20T13:41:17+08:00"
    assert to_beijing_timestamp("2026-07-20T13:41:17+08:00") == "2026-07-20T13:41:17+08:00"


def test_existing_schema_is_upgraded_without_losing_rows():
    connection = sqlite3.connect(":memory:")
    connection.executescript('''
        CREATE TABLE companies(code TEXT PRIMARY KEY, raw_code TEXT, name TEXT, market TEXT, industry_name TEXT, updated_at TEXT);
        INSERT INTO companies VALUES ('SH600056', '600056', '中国医药', 'SH', NULL, '2026-01-01T00:00:00+08:00');
    ''')
    ensure_normalized_schema(connection)
    company_columns = {row[1] for row in connection.execute("PRAGMA table_info(companies)")}
    balance_columns = {row[1] for row in connection.execute("PRAGMA table_info(balance_sheets)")}
    assert "business_model" in company_columns
    assert {"monetary_funds", "inventory", "accounts_payable", "current_assets", "current_liabilities", "equity_attributable_to_parent"} <= balance_columns
    assert connection.execute("SELECT name FROM companies WHERE code='SH600056'").fetchone()[0] == "中国医药"

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Mapping
from zoneinfo import ZoneInfo

from financial_normalization import (
    infer_report_type,
    normalize_report_period,
    normalize_security_code,
    parse_amount_to_yuan,
    parse_percentage_points,
)


SCHEMA_VERSION = 2
BEIJING_TIMEZONE = ZoneInfo("Asia/Shanghai")

INCOME_AMOUNT_FIELDS = {
    "net_profit": "net_profit",
    "total_operating_income": "total_operating_income",
    "total_operating_cost": "total_operating_cost",
    "sales_expenses": "sales_expenses",
    "management_expenses": "management_expenses",
    "financial_expenses": "financial_expenses",
    "operating_costs": "operating_cost",
    "operating_profit": "operating_profit",
    "total_profit": "total_profit",
    "RandD_expenses": "research_and_development_expenses",
    "business_tax_and_surcharges": "business_tax_and_surcharges",
    "interest_expenses": "interest_expenses",
    "interest_income": "interest_income",
    "gross_profit": "gross_profit",
    "netProfitFromOngoingOperations": "net_profit_from_ongoing_operations",
    "netProfitAttributableToTheParentCompany": "net_profit_attributable_to_parent",
    "netProfitAfterDeductingNonRecurringGainsAndLosses": "net_profit_after_non_recurring",
    "income_tax_expense": "income_tax_expense",
    "investment_income": "investment_income",
    "asset_impairment_loss": "asset_impairment_loss",
    "credit_impairment_loss": "credit_impairment_loss",
}
INCOME_RATIO_FIELDS = {
    "gross_profit_margin": "gross_profit_margin",
    "yearOnYearGrowthInTotalOperatingRevenue": "revenue_yoy_growth",
}
BALANCE_AMOUNT_FIELDS = {
    "total_assets": "total_assets",
    "total_liabilities": "total_liabilities",
    "paid_in_capital": "paid_in_capital",
    "capital_reserve": "capital_reserve",
    "other_comprehensive_income": "other_comprehensive_income",
    "surplus_reserve": "surplus_reserve",
    "undistributed_profits": "undistributed_profits",
    "minority_shareholder_equity": "minority_shareholder_equity",
    "accounts_receivable": "accounts_receivable",
    "monetary_funds": "monetary_funds",
    "inventory": "inventory",
    "accounts_payable": "accounts_payable",
    "current_assets": "current_assets",
    "current_liabilities": "current_liabilities",
    "short_term_borrowings": "short_term_borrowings",
    "long_term_borrowings": "long_term_borrowings",
    "total_equity": "total_equity",
    "equity_attributable_to_parent": "equity_attributable_to_parent",
    "goodwill": "goodwill",
}
CASH_FLOW_AMOUNT_FIELDS = {
    "net_operating_cash_flow": "net_operating_cash_flow",
    "net_investing_cash_flow": "net_investing_cash_flow",
    "net_financing_cash_flow": "net_financing_cash_flow",
    "cash_received_from_sales": "cash_received_from_sales",
    "capital_expenditure": "capital_expenditure",
    "ending_cash_and_equivalents": "ending_cash_and_equivalents",
}


def beijing_now() -> str:
    return datetime.now(BEIJING_TIMEZONE).isoformat(timespec="seconds")


def to_beijing_timestamp(value: str | None) -> str | None:
    if not value:
        return value
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=BEIJING_TIMEZONE)
    else:
        parsed = parsed.astimezone(BEIJING_TIMEZONE)
    return parsed.isoformat(timespec="seconds")


def ensure_normalized_schema(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        '''
        CREATE TABLE IF NOT EXISTS companies (
            code TEXT PRIMARY KEY,
            raw_code TEXT NOT NULL,
            name TEXT NOT NULL,
            market TEXT NOT NULL CHECK (market IN ('SH', 'SZ')),
            industry_name TEXT,
            business_model TEXT,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS import_batches (
            batch_id TEXT PRIMARY KEY,
            source_name TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            status TEXT NOT NULL,
            raw_row_count INTEGER NOT NULL DEFAULT 0,
            normalized_row_count INTEGER NOT NULL DEFAULT 0,
            issue_count INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS income_statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL REFERENCES companies(code),
            report_period TEXT NOT NULL,
            report_type TEXT NOT NULL CHECK (report_type IN ('Q1', 'H1', 'Q3', 'FY')),
            currency TEXT NOT NULL DEFAULT 'CNY',
            net_profit INTEGER,
            total_operating_income INTEGER,
            total_operating_cost INTEGER,
            operating_cost INTEGER,
            sales_expenses INTEGER,
            management_expenses INTEGER,
            financial_expenses INTEGER,
            research_and_development_expenses INTEGER,
            business_tax_and_surcharges INTEGER,
            operating_profit INTEGER,
            total_profit INTEGER,
            interest_expenses INTEGER,
            interest_income INTEGER,
            gross_profit INTEGER,
            gross_profit_margin REAL,
            net_profit_from_ongoing_operations INTEGER,
            net_profit_attributable_to_parent INTEGER,
            net_profit_after_non_recurring INTEGER,
            revenue_yoy_growth REAL,
            income_tax_expense INTEGER,
            investment_income INTEGER,
            asset_impairment_loss INTEGER,
            credit_impairment_loss INTEGER,
            source_record_id INTEGER,
            import_batch_id TEXT REFERENCES import_batches(batch_id),
            collected_at TEXT NOT NULL,
            UNIQUE (code, report_period)
        );
        CREATE TABLE IF NOT EXISTS balance_sheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL REFERENCES companies(code),
            report_period TEXT NOT NULL,
            report_type TEXT NOT NULL CHECK (report_type IN ('Q1', 'H1', 'Q3', 'FY')),
            currency TEXT NOT NULL DEFAULT 'CNY',
            total_assets INTEGER,
            total_liabilities INTEGER,
            paid_in_capital INTEGER,
            capital_reserve INTEGER,
            other_comprehensive_income INTEGER,
            surplus_reserve INTEGER,
            undistributed_profits INTEGER,
            minority_shareholder_equity INTEGER,
            accounts_receivable INTEGER,
            monetary_funds INTEGER,
            inventory INTEGER,
            accounts_payable INTEGER,
            current_assets INTEGER,
            current_liabilities INTEGER,
            short_term_borrowings INTEGER,
            long_term_borrowings INTEGER,
            total_equity INTEGER,
            equity_attributable_to_parent INTEGER,
            goodwill INTEGER,
            source_record_id INTEGER,
            import_batch_id TEXT REFERENCES import_batches(batch_id),
            collected_at TEXT NOT NULL,
            UNIQUE (code, report_period)
        );
        CREATE TABLE IF NOT EXISTS cash_flow_statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL REFERENCES companies(code),
            report_period TEXT NOT NULL,
            report_type TEXT NOT NULL CHECK (report_type IN ('Q1', 'H1', 'Q3', 'FY')),
            currency TEXT NOT NULL DEFAULT 'CNY',
            net_operating_cash_flow INTEGER,
            net_investing_cash_flow INTEGER,
            net_financing_cash_flow INTEGER,
            cash_received_from_sales INTEGER,
            capital_expenditure INTEGER,
            ending_cash_and_equivalents INTEGER,
            source_record_id INTEGER,
            import_batch_id TEXT REFERENCES import_batches(batch_id),
            collected_at TEXT NOT NULL,
            UNIQUE (code, report_period)
        );
        CREATE TABLE IF NOT EXISTS data_quality_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT REFERENCES import_batches(batch_id),
            statement_type TEXT NOT NULL,
            code TEXT,
            report_period TEXT,
            field_name TEXT NOT NULL,
            raw_value TEXT,
            issue_code TEXT NOT NULL,
            issue_message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_income_period ON income_statements(report_period);
        CREATE INDEX IF NOT EXISTS idx_balance_period ON balance_sheets(report_period);
        CREATE INDEX IF NOT EXISTS idx_cash_flow_period ON cash_flow_statements(report_period);
        CREATE INDEX IF NOT EXISTS idx_quality_batch ON data_quality_issues(batch_id);
        '''
    )
    upgrades = {
        "companies": {"business_model": "TEXT"},
        "income_statements": {
            "income_tax_expense": "INTEGER", "investment_income": "INTEGER",
            "asset_impairment_loss": "INTEGER", "credit_impairment_loss": "INTEGER",
        },
        "balance_sheets": {
            "monetary_funds": "INTEGER", "inventory": "INTEGER", "accounts_payable": "INTEGER",
            "current_assets": "INTEGER", "current_liabilities": "INTEGER",
            "short_term_borrowings": "INTEGER", "long_term_borrowings": "INTEGER",
            "total_equity": "INTEGER", "equity_attributable_to_parent": "INTEGER", "goodwill": "INTEGER",
        },
    }
    for table, columns in upgrades.items():
        existing = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
        for column, sql_type in columns.items():
            if column not in existing:
                connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}")
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def _as_mapping(raw_row: Mapping | sqlite3.Row) -> Mapping:
    return raw_row


def _record_issue(
    connection: sqlite3.Connection,
    batch_id: str,
    statement_type: str,
    code: str | None,
    period: str | None,
    field_name: str,
    raw_value: object,
) -> None:
    marker = "MISSING_VALUE" if raw_value is None or str(raw_value).strip() in {"", "--", "-"} else "INVALID_VALUE"
    connection.execute(
        '''INSERT INTO data_quality_issues
           (batch_id, statement_type, code, report_period, field_name, raw_value,
            issue_code, issue_message, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            batch_id,
            statement_type,
            code,
            period,
            field_name,
            None if raw_value is None else str(raw_value),
            marker,
            "原始字段为空" if marker == "MISSING_VALUE" else "原始字段无法解析",
            beijing_now(),
        ),
    )


def _upsert_company(connection: sqlite3.Connection, row: Mapping) -> tuple[str, str]:
    code, market = normalize_security_code(row["code"])
    connection.execute(
        '''INSERT INTO companies(code, raw_code, name, market, updated_at)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(code) DO UPDATE SET
             raw_code=excluded.raw_code, name=excluded.name,
             market=excluded.market, updated_at=excluded.updated_at''',
        (code, str(row["code"]), str(row["name"]).strip(), market, beijing_now()),
    )
    return code, market


def upsert_income_statement(connection: sqlite3.Connection, raw_row: Mapping, batch_id: str) -> None:
    row = _as_mapping(raw_row)
    code, _ = _upsert_company(connection, row)
    period = normalize_report_period(row["disclosure_date"])
    report_type = infer_report_type(period)
    if not period or not report_type:
        _record_issue(connection, batch_id, "income", code, period, "disclosure_date", row["disclosure_date"])
        return
    values: dict[str, object] = {}
    for source, target in INCOME_AMOUNT_FIELDS.items():
        if source not in row.keys():
            continue
        raw_value = row[source]
        values[target] = parse_amount_to_yuan(raw_value)
        if source in row.keys() and values[target] is None:
            _record_issue(connection, batch_id, "income", code, period, target, raw_value)
    for source, target in INCOME_RATIO_FIELDS.items():
        if source not in row.keys():
            continue
        raw_value = row[source]
        values[target] = parse_percentage_points(raw_value)
        if source in row.keys() and values[target] is None:
            _record_issue(connection, batch_id, "income", code, period, target, raw_value)
    columns = list(values)
    placeholders = ", ".join("?" for _ in columns)
    update_clause = ", ".join(f"{column}=excluded.{column}" for column in columns)
    connection.execute(
        f'''INSERT INTO income_statements
            (code, report_period, report_type, currency, {", ".join(columns)},
             source_record_id, import_batch_id, collected_at)
            VALUES (?, ?, ?, 'CNY', {placeholders}, ?, ?, ?)
            ON CONFLICT(code, report_period) DO UPDATE SET
              report_type=excluded.report_type, {update_clause},
              source_record_id=excluded.source_record_id,
              import_batch_id=excluded.import_batch_id,
              collected_at=excluded.collected_at''',
        (code, period, report_type, *(values[column] for column in columns), row["id"] if "id" in row.keys() else None, batch_id, beijing_now()),
    )


def upsert_balance_sheet(connection: sqlite3.Connection, raw_row: Mapping, batch_id: str) -> None:
    row = _as_mapping(raw_row)
    code, _ = _upsert_company(connection, row)
    period = normalize_report_period(row["disclosure_date"])
    report_type = infer_report_type(period)
    if not period or not report_type:
        _record_issue(connection, batch_id, "balance", code, period, "disclosure_date", row["disclosure_date"])
        return
    values: dict[str, object] = {}
    for source, target in BALANCE_AMOUNT_FIELDS.items():
        if source not in row.keys():
            continue
        raw_value = row[source]
        values[target] = parse_amount_to_yuan(raw_value)
        if source in row.keys() and values[target] is None:
            _record_issue(connection, batch_id, "balance", code, period, target, raw_value)
    columns = list(values)
    placeholders = ", ".join("?" for _ in columns)
    update_clause = ", ".join(f"{column}=excluded.{column}" for column in columns)
    connection.execute(
        f'''INSERT INTO balance_sheets
            (code, report_period, report_type, currency, {", ".join(columns)},
             source_record_id, import_batch_id, collected_at)
            VALUES (?, ?, ?, 'CNY', {placeholders}, ?, ?, ?)
            ON CONFLICT(code, report_period) DO UPDATE SET
              report_type=excluded.report_type, {update_clause},
              source_record_id=excluded.source_record_id,
              import_batch_id=excluded.import_batch_id,
              collected_at=excluded.collected_at''',
        (code, period, report_type, *(values[column] for column in columns), row["id"] if "id" in row.keys() else None, batch_id, beijing_now()),
    )


def upsert_cash_flow_statement(connection: sqlite3.Connection, raw_row: Mapping, batch_id: str) -> None:
    row = _as_mapping(raw_row)
    code, _ = _upsert_company(connection, row)
    period = normalize_report_period(row["disclosure_date"])
    report_type = infer_report_type(period)
    if not period or not report_type:
        _record_issue(connection, batch_id, "cash_flow", code, period, "disclosure_date", row["disclosure_date"])
        return
    values = {
        target: parse_amount_to_yuan(row[source])
        for source, target in CASH_FLOW_AMOUNT_FIELDS.items()
        if source in row.keys()
    }
    for source, target in CASH_FLOW_AMOUNT_FIELDS.items():
        raw_value = row[source] if source in row.keys() else None
        if source in row.keys() and values[target] is None:
            _record_issue(connection, batch_id, "cash_flow", code, period, target, raw_value)
    columns = list(values)
    placeholders = ", ".join("?" for _ in columns)
    update_clause = ", ".join(f"{column}=excluded.{column}" for column in columns)
    connection.execute(
        f'''INSERT INTO cash_flow_statements
            (code, report_period, report_type, currency, {", ".join(columns)},
             source_record_id, import_batch_id, collected_at)
            VALUES (?, ?, ?, 'CNY', {placeholders}, ?, ?, ?)
            ON CONFLICT(code, report_period) DO UPDATE SET
              report_type=excluded.report_type, {update_clause},
              source_record_id=excluded.source_record_id,
              import_batch_id=excluded.import_batch_id,
              collected_at=excluded.collected_at''',
        (code, period, report_type, *(values[column] for column in columns), row["id"] if "id" in row.keys() else None, batch_id, beijing_now()),
    )

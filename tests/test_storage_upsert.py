import sqlite3

import pytest

from selenium_spyder import INCOME_ROW_LABELS
from sqlserver_operation import insert_lrb


def create_raw_income_table(database_path):
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            '''CREATE TABLE "利润表temp" (
                id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, name TEXT,
                net_profit TEXT, total_operating_income TEXT, total_operating_cost TEXT,
                sales_expenses TEXT, management_expenses TEXT, financial_expenses TEXT,
                operating_costs TEXT, operating_profit TEXT, total_profit TEXT,
                disclosure_date TEXT, RandD_expenses TEXT,
                business_tax_and_surcharges TEXT, insert_batch TEXT,
                interest_expenses TEXT, interest_income TEXT, gross_profit TEXT,
                gross_profit_margin TEXT, netProfitFromOngoingOperations TEXT,
                netProfitAttributableToTheParentCompany TEXT,
                netProfitAfterDeductingNonRecurringGainsAndLosses TEXT,
                yearOnYearGrowthInTotalOperatingRevenue TEXT
            )'''
        )


def income_row(net_profit):
    return (
        "000705", "浙江震元", net_profit, "10亿", "8亿", "100万", "200万",
        "-50万", "7亿", "3000万", "2500万", "2026-03-31", "120万", "30万",
        "batch-test", "20万", "70万", "2亿", "20%", net_profit, net_profit,
        net_profit, "6.36%",
    )


def test_insert_lrb_writes_raw_and_updates_normalized_record(tmp_path, monkeypatch):
    database_path = tmp_path / "storage.db"
    create_raw_income_table(database_path)
    monkeypatch.setenv("FINANCIAL_DB_PATH", str(database_path))
    insert_lrb([income_row("-2181万")])
    insert_lrb([income_row("-2000万")])
    with sqlite3.connect(database_path) as connection:
        assert connection.execute('SELECT COUNT(*) FROM "利润表temp"').fetchone()[0] == 1
        assert connection.execute(
            "SELECT net_profit FROM income_statements WHERE code='SZ000705' AND report_period='2026-03-31'"
        ).fetchone()[0] == -20_000_000


def test_income_row_labels_keep_operating_cost_separate():
    assert INCOME_ROW_LABELS["total_operating_cost"] == "营业总成本"
    assert INCOME_ROW_LABELS["operating_cost"] == "营业成本"
    assert INCOME_ROW_LABELS["total_operating_cost"] != INCOME_ROW_LABELS["operating_cost"]

import sqlite3

from migrate_financial_data import migrate_database, repair_database_metadata


def build_raw_fixture_database(tmp_path):
    database_path = tmp_path / "fixture.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            '''CREATE TABLE "利润表temp" (
                id INTEGER PRIMARY KEY, code TEXT, name TEXT, net_profit TEXT,
                total_operating_income TEXT, total_operating_cost TEXT,
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
        connection.execute(
            '''CREATE TABLE "资产负债表temp" (
                id INTEGER PRIMARY KEY, code TEXT, name TEXT, total_assets TEXT,
                total_liabilities TEXT, paid_in_capital TEXT, capital_reserve TEXT,
                other_comprehensive_income TEXT, surplus_reserve TEXT,
                undistributed_profits TEXT, minority_shareholder_equity TEXT,
                disclosure_date TEXT, insert_batch TEXT, accounts_receivable TEXT
            )'''
        )
        income = (
            1, "000705", "浙江震元", "-2181万", "10亿", "8亿", "100万", "200万",
            "-50万", "7亿", "3000万", "2500万", "2026/03/31", "120万", "30万",
            "batch-1", "20万", "70万", "2亿", "20%", "-2181万", "-2200万",
            "-2300万", "6.36%",
        )
        connection.execute('INSERT INTO "利润表temp" VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', income)
        connection.execute('INSERT INTO "利润表temp" VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (2, *income[1:]))
        connection.execute(
            'INSERT INTO "资产负债表temp" VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (1, "000705", "浙江震元", "50亿", "30亿", "1亿", "2亿", "--", "1亿", "5亿", "1亿", "2026/03/31", "batch-1", "3亿"),
        )
    return database_path


def test_migration_keeps_negative_values_and_is_idempotent(tmp_path):
    database_path = build_raw_fixture_database(tmp_path)
    first = migrate_database(database_path)
    second = migrate_database(database_path)
    assert first.income_rows == 1
    assert second.income_rows == 1
    with sqlite3.connect(database_path) as connection:
        value = connection.execute(
            "SELECT net_profit FROM income_statements WHERE code=? AND report_period=?",
            ("SZ000705", "2026-03-31"),
        ).fetchone()[0]
    assert value == -21_810_000


def test_migration_records_invalid_values_as_quality_issues(tmp_path):
    database_path = build_raw_fixture_database(tmp_path)
    migrate_database(database_path)
    with sqlite3.connect(database_path) as connection:
        issue = connection.execute(
            "SELECT field_name, issue_code FROM data_quality_issues WHERE raw_value='--'"
        ).fetchone()
    assert issue == ("other_comprehensive_income", "MISSING_VALUE")


def test_repair_metadata_converts_timezone_and_completes_legacy_batch(tmp_path):
    database_path = build_raw_fixture_database(tmp_path)
    migrate_database(database_path)
    with sqlite3.connect(database_path) as connection:
        connection.execute('UPDATE "利润表temp" SET insert_batch=?', ("legacy-running",))
        connection.execute(
            '''INSERT INTO import_batches
               (batch_id, source_name, started_at, status, raw_row_count, normalized_row_count, issue_count)
               VALUES ('legacy-running', 'selenium-income-statement',
                       '2026-07-20T05:41:17+00:00', 'running', 0, 0, 0)'''
        )
        connection.execute("UPDATE companies SET updated_at='2026-07-20T05:41:17+00:00'")
        connection.execute("UPDATE income_statements SET collected_at='2026-07-20T05:41:18+00:00'")
    result = repair_database_metadata(database_path)
    assert result.completed_batches == 1
    with sqlite3.connect(database_path) as connection:
        batch = connection.execute(
            "SELECT status, raw_row_count, normalized_row_count, started_at, completed_at "
            "FROM import_batches WHERE batch_id='legacy-running'"
        ).fetchone()
        company_time = connection.execute("SELECT updated_at FROM companies LIMIT 1").fetchone()[0]
    assert batch[:3] == ("completed", 2, 1)
    assert batch[3] == "2026-07-20T13:41:17+08:00"
    assert batch[4].endswith("+08:00")
    assert company_time == "2026-07-20T13:41:17+08:00"

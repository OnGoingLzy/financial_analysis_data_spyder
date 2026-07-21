import os
import sqlite3
from collections import Counter
from pathlib import Path

from financial_schema import beijing_now, ensure_normalized_schema, upsert_balance_sheet, upsert_cash_flow_statement, upsert_income_statement


DEFAULT_DATABASE_PATH = Path(__file__).resolve().with_name("financial_analysis.db")


def get_connection(database_path=None):
    resolved_path = database_path or os.environ.get("FINANCIAL_DB_PATH") or DEFAULT_DATABASE_PATH
    connection = sqlite3.connect(resolved_path)
    connection.row_factory = sqlite3.Row
    return connection


# 日志写入数据库
def Log(lx, page, action, msg):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        sql_string = "insert into t_hz_spyder_dd_log(lx,page,action,msg) values(?, ?, ?, ?)"
        lst = [lx, page, action, msg]
        connection.execute(sql_string, lst)
        connection.commit()
    except Exception as e:
        print(e)
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def _ensure_import_batch(connection, batch_id, source_name):
    connection.execute(
        '''INSERT OR IGNORE INTO import_batches
           (batch_id, source_name, started_at, status, raw_row_count, normalized_row_count, issue_count)
           VALUES (?, ?, ?, 'running', 0, 0, 0)''',
        (str(batch_id), source_name, beijing_now()),
    )


def _row_dict(columns, values):
    return dict(zip(columns, values))


def _ensure_raw_columns(connection, table_name, columns):
    """为历史原始表补充新采集字段，保留原表与已有数据。"""
    existing = {
        row[1] for row in connection.execute(f'PRAGMA table_info("{table_name}")')
    }
    for column in columns:
        if column not in existing:
            connection.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{column}" TEXT')


def _pad_rows(rows, size):
    """兼容旧调用方的短元组；未提供的新字段按 NULL 写入。"""
    return [tuple(values) + (None,) * (size - len(values)) for values in rows]


def _complete_import_batches(connection, rows, normalized_table):
    batch_counts = Counter(str(row["insert_batch"]) for row in rows)
    for batch_id, raw_count in batch_counts.items():
        normalized_count = connection.execute(
            f"SELECT COUNT(*) FROM {normalized_table} WHERE import_batch_id = ?",
            (batch_id,),
        ).fetchone()[0]
        issue_count = connection.execute(
            "SELECT COUNT(*) FROM data_quality_issues WHERE batch_id = ?",
            (batch_id,),
        ).fetchone()[0]
        connection.execute(
            '''UPDATE import_batches
               SET completed_at=?, status='completed', raw_row_count=?,
                   normalized_row_count=?, issue_count=?
               WHERE batch_id=?''',
            (beijing_now(), raw_count, normalized_count, issue_count, batch_id),
        )


def insert_zcfzb(data):
    connection = None
    cursor = None
    try:
        data = list(data)
        connection = get_connection()
        cursor = connection.cursor()
        ensure_normalized_schema(connection)
        columns = [
            "code", "name", "total_assets", "total_liabilities", "paid_in_capital",
            "capital_reserve", "other_comprehensive_income", "surplus_reserve",
            "undistributed_profits", "minority_shareholder_equity", "disclosure_date",
            "insert_batch", "accounts_receivable", "monetary_funds", "inventory",
            "accounts_payable", "current_assets", "current_liabilities",
            "short_term_borrowings", "long_term_borrowings", "total_equity",
            "equity_attributable_to_parent", "goodwill",
        ]
        _ensure_raw_columns(connection, "资产负债表temp", columns)
        raw_data = _pad_rows(data, len(columns))

        # 创建唯一索引，防止code和disclosure_date重复
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_zcfzb_code_disclosure_date 
            ON 资产负债表temp(code, disclosure_date)
        ''')
        
        # 使用INSERT OR IGNORE防止重复插入
        quoted_columns = ",".join(f'"{column}"' for column in columns)
        placeholders = ",".join("?" for _ in columns)
        sql_string = f'INSERT OR IGNORE INTO "资产负债表temp" ({quoted_columns}) VALUES ({placeholders})'
        cursor.executemany(sql_string, raw_data)
        normalized_rows = []
        for values in data:
            row = _row_dict(columns, values)
            normalized_rows.append(row)
            batch_id = str(row["insert_batch"])
            _ensure_import_batch(connection, batch_id, "selenium-balance-sheet")
            upsert_balance_sheet(connection, row, batch_id)
        _complete_import_batches(connection, normalized_rows, "balance_sheets")
        connection.commit()
    except Exception as e:
        if connection is not None:
            connection.rollback()
        print(e)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def insert_lrb(data):
    connection = None
    cursor = None
    try:
        data = list(data)
        connection = get_connection()
        cursor = connection.cursor()
        ensure_normalized_schema(connection)
        columns = [
            "code", "name", "net_profit", "total_operating_income", "total_operating_cost",
            "sales_expenses", "management_expenses", "financial_expenses", "operating_costs",
            "operating_profit", "total_profit", "disclosure_date", "RandD_expenses",
            "business_tax_and_surcharges", "insert_batch", "interest_expenses",
            "interest_income", "gross_profit", "gross_profit_margin",
            "netProfitFromOngoingOperations", "netProfitAttributableToTheParentCompany",
            "netProfitAfterDeductingNonRecurringGainsAndLosses",
            "yearOnYearGrowthInTotalOperatingRevenue", "income_tax_expense",
            "investment_income", "asset_impairment_loss", "credit_impairment_loss",
        ]
        _ensure_raw_columns(connection, "利润表temp", columns)
        raw_data = _pad_rows(data, len(columns))
        # 创建唯一索引，防止code和disclosure_date重复
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_lrb_code_disclosure_date
            ON 利润表temp(code, disclosure_date)
        ''')

        # 使用INSERT OR IGNORE防止重复插入
        quoted_columns = ",".join(f'"{column}"' for column in columns)
        placeholders = ",".join("?" for _ in columns)
        sql_string = f'INSERT OR IGNORE INTO "利润表temp" ({quoted_columns}) VALUES ({placeholders})'
        cursor.executemany(sql_string, raw_data)
        normalized_rows = []
        for values in data:
            row = _row_dict(columns, values)
            normalized_rows.append(row)
            batch_id = str(row["insert_batch"])
            _ensure_import_batch(connection, batch_id, "selenium-income-statement")
            upsert_income_statement(connection, row, batch_id)
        _complete_import_batches(connection, normalized_rows, "income_statements")
        connection.commit()
    except Exception as e:
        if connection is not None:
            connection.rollback()
        print(e)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def insert_xjllb(data):
    data = list(data)
    connection = get_connection()
    try:
        ensure_normalized_schema(connection)
        connection.execute('''CREATE TABLE IF NOT EXISTS "现金流量表temp" (
            id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, name TEXT,
            net_operating_cash_flow TEXT, net_investing_cash_flow TEXT,
            net_financing_cash_flow TEXT, cash_received_from_sales TEXT,
            capital_expenditure TEXT, ending_cash_and_equivalents TEXT,
            disclosure_date TEXT, insert_batch TEXT,
            UNIQUE(code, disclosure_date)
        )''')
        columns = [
            "code", "name", "net_operating_cash_flow", "net_investing_cash_flow",
            "net_financing_cash_flow", "cash_received_from_sales", "capital_expenditure",
            "ending_cash_and_equivalents", "disclosure_date", "insert_batch",
        ]
        connection.executemany(
            '''INSERT OR IGNORE INTO "现金流量表temp"
               (code,name,net_operating_cash_flow,net_investing_cash_flow,net_financing_cash_flow,
                cash_received_from_sales,capital_expenditure,ending_cash_and_equivalents,
                disclosure_date,insert_batch) VALUES (?,?,?,?,?,?,?,?,?,?)''',
            data,
        )
        rows = [_row_dict(columns, values) for values in data]
        for row in rows:
            batch_id = str(row["insert_batch"])
            _ensure_import_batch(connection, batch_id, "selenium-cash-flow-statement")
            upsert_cash_flow_statement(connection, row, batch_id)
        _complete_import_batches(connection, rows, "cash_flow_statements")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

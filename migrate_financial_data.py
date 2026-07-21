from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from financial_normalization import normalize_report_period, normalize_security_code
from financial_schema import (
    ensure_normalized_schema,
    to_beijing_timestamp,
    upsert_balance_sheet,
    upsert_income_statement,
    beijing_now,
)


@dataclass(frozen=True)
class MigrationResult:
    companies: int
    income_rows: int
    balance_rows: int
    issue_count: int
    backup_path: str | None = None


@dataclass(frozen=True)
class MetadataRepairResult:
    timestamps_updated: int
    completed_batches: int
    backup_path: str | None = None


def upgrade_database_schema(
    database_path: str | Path,
    backup_path: str | Path | None = None,
) -> int:
    """仅升级标准表结构，不重复迁移历史原始数据。"""
    database_path = Path(database_path).resolve()
    if not database_path.exists():
        raise FileNotFoundError(f"未找到数据库：{database_path}")
    resolved_backup = Path(backup_path).resolve() if backup_path else None
    if resolved_backup:
        _create_backup(database_path, resolved_backup)
    with sqlite3.connect(database_path) as connection:
        ensure_normalized_schema(connection)
        return connection.execute("PRAGMA user_version").fetchone()[0]


def _create_backup(source_path: Path, backup_path: Path) -> None:
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source_path) as source, sqlite3.connect(backup_path) as target:
        source.backup(target)


def migrate_database(database_path: str | Path, backup_path: str | Path | None = None) -> MigrationResult:
    database_path = Path(database_path).resolve()
    if not database_path.exists():
        raise FileNotFoundError(f"未找到数据库：{database_path}")
    resolved_backup = Path(backup_path).resolve() if backup_path else None
    if resolved_backup:
        _create_backup(database_path, resolved_backup)

    batch_id = f"migration-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        ensure_normalized_schema(connection)
        income_rows = list(connection.execute('SELECT * FROM "利润表temp" ORDER BY id'))
        balance_rows = list(connection.execute('SELECT * FROM "资产负债表temp" ORDER BY id'))
        connection.execute(
            '''INSERT INTO import_batches
               (batch_id, source_name, started_at, status, raw_row_count, normalized_row_count, issue_count)
               VALUES (?, 'legacy-sqlite-migration', ?, 'running', ?, 0, 0)''',
            (batch_id, beijing_now(), len(income_rows) + len(balance_rows)),
        )
        for row in income_rows:
            upsert_income_statement(connection, row, batch_id)
        for row in balance_rows:
            upsert_balance_sheet(connection, row, batch_id)
        counts = {
            "companies": connection.execute("SELECT COUNT(*) FROM companies").fetchone()[0],
            "income": connection.execute("SELECT COUNT(*) FROM income_statements").fetchone()[0],
            "balance": connection.execute("SELECT COUNT(*) FROM balance_sheets").fetchone()[0],
            "issues": connection.execute("SELECT COUNT(*) FROM data_quality_issues WHERE batch_id=?", (batch_id,)).fetchone()[0],
        }
        connection.execute(
            '''UPDATE import_batches SET completed_at=?, status='completed',
               normalized_row_count=?, issue_count=? WHERE batch_id=?''',
            (beijing_now(), counts["income"] + counts["balance"], counts["issues"], batch_id),
        )
    return MigrationResult(
        companies=counts["companies"],
        income_rows=counts["income"],
        balance_rows=counts["balance"],
        issue_count=counts["issues"],
        backup_path=str(resolved_backup) if resolved_backup else None,
    )


def _convert_timestamp_column(connection: sqlite3.Connection, table: str, column: str) -> int:
    rows = connection.execute(
        f"SELECT rowid, {column} FROM {table} WHERE {column} IS NOT NULL"
    ).fetchall()
    updated = 0
    for rowid, value in rows:
        converted = to_beijing_timestamp(value)
        if converted != value:
            connection.execute(
                f"UPDATE {table} SET {column}=? WHERE rowid=?",
                (converted, rowid),
            )
            updated += 1
    return updated


def _count_normalized_rows_for_batch(
    connection: sqlite3.Connection,
    batch_id: str,
    raw_table: str,
    normalized_table: str,
) -> tuple[int, int, str | None]:
    raw_rows = connection.execute(
        f'''SELECT code, disclosure_date FROM "{raw_table}"
            WHERE CAST(insert_batch AS TEXT)=?''',
        (batch_id,),
    ).fetchall()
    normalized_keys = set()
    latest_collected_at = None
    for raw_code, raw_period in raw_rows:
        try:
            code, _ = normalize_security_code(raw_code)
        except ValueError:
            continue
        period = normalize_report_period(raw_period)
        if not period:
            continue
        normalized = connection.execute(
            f'''SELECT collected_at FROM {normalized_table}
                WHERE code=? AND report_period=?''',
            (code, period),
        ).fetchone()
        if normalized:
            normalized_keys.add((code, period))
            if normalized[0] and (latest_collected_at is None or normalized[0] > latest_collected_at):
                latest_collected_at = normalized[0]
    return len(raw_rows), len(normalized_keys), latest_collected_at


def repair_database_metadata(
    database_path: str | Path,
    backup_path: str | Path | None = None,
) -> MetadataRepairResult:
    database_path = Path(database_path).resolve()
    if not database_path.exists():
        raise FileNotFoundError(f"未找到数据库：{database_path}")
    resolved_backup = Path(backup_path).resolve() if backup_path else None
    if resolved_backup:
        _create_backup(database_path, resolved_backup)

    timestamp_fields = (
        ("companies", "updated_at"),
        ("import_batches", "started_at"),
        ("import_batches", "completed_at"),
        ("income_statements", "collected_at"),
        ("balance_sheets", "collected_at"),
        ("cash_flow_statements", "collected_at"),
        ("data_quality_issues", "created_at"),
    )
    completed_batches = 0
    with sqlite3.connect(database_path) as connection:
        ensure_normalized_schema(connection)
        timestamps_updated = sum(
            _convert_timestamp_column(connection, table, column)
            for table, column in timestamp_fields
        )
        running_batches = connection.execute(
            "SELECT batch_id, source_name, started_at FROM import_batches WHERE status='running'"
        ).fetchall()
        for batch_id, source_name, started_at in running_batches:
            if source_name == "selenium-income-statement":
                raw_table, normalized_table = "利润表temp", "income_statements"
            elif source_name == "selenium-balance-sheet":
                raw_table, normalized_table = "资产负债表temp", "balance_sheets"
            else:
                continue
            raw_count, normalized_count, latest_collected_at = _count_normalized_rows_for_batch(
                connection, batch_id, raw_table, normalized_table
            )
            issue_count = connection.execute(
                "SELECT COUNT(*) FROM data_quality_issues WHERE batch_id=?",
                (batch_id,),
            ).fetchone()[0]
            completed_at = to_beijing_timestamp(latest_collected_at) or started_at or beijing_now()
            connection.execute(
                '''UPDATE import_batches
                   SET completed_at=?, status='completed', raw_row_count=?,
                       normalized_row_count=?, issue_count=?
                   WHERE batch_id=?''',
                (completed_at, raw_count, normalized_count, issue_count, batch_id),
            )
            completed_batches += 1
    return MetadataRepairResult(
        timestamps_updated=timestamps_updated,
        completed_batches=completed_batches,
        backup_path=str(resolved_backup) if resolved_backup else None,
    )


def verify_database(database_path: str | Path) -> dict[str, int | bool]:
    with sqlite3.connect(Path(database_path).resolve()) as connection:
        return {
            "companies": connection.execute("SELECT COUNT(*) FROM companies").fetchone()[0],
            "income_statements": connection.execute("SELECT COUNT(*) FROM income_statements").fetchone()[0],
            "balance_sheets": connection.execute("SELECT COUNT(*) FROM balance_sheets").fetchone()[0],
            "cash_flow_statements": connection.execute("SELECT COUNT(*) FROM cash_flow_statements").fetchone()[0],
            "negative_financial_expenses": connection.execute("SELECT COUNT(*) FROM income_statements WHERE financial_expenses < 0").fetchone()[0],
            "duplicate_income_periods": connection.execute("SELECT COUNT(*) FROM (SELECT code, report_period FROM income_statements GROUP BY code, report_period HAVING COUNT(*) > 1)").fetchone()[0],
            "duplicate_balance_periods": connection.execute("SELECT COUNT(*) FROM (SELECT code, report_period FROM balance_sheets GROUP BY code, report_period HAVING COUNT(*) > 1)").fetchone()[0],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="迁移并验证标准化财务数据")
    parser.add_argument("--database", required=True)
    parser.add_argument("--backup")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--repair-metadata", action="store_true")
    parser.add_argument("--upgrade-schema", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        print(verify_database(args.database))
        return
    if args.repair_metadata:
        result = repair_database_metadata(args.database, args.backup)
        print(
            f"timestamps_updated={result.timestamps_updated}, "
            f"completed_batches={result.completed_batches}"
        )
        return
    if args.upgrade_schema:
        version = upgrade_database_schema(args.database, args.backup)
        print(f"schema_version={version}")
        return
    result = migrate_database(args.database, args.backup)
    print(
        f"companies={result.companies}, income_statements={result.income_rows}, "
        f"balance_sheets={result.balance_rows}, issues={result.issue_count}"
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from financial_schema import ensure_normalized_schema, upsert_balance_sheet, upsert_income_statement, utc_now


@dataclass(frozen=True)
class MigrationResult:
    companies: int
    income_rows: int
    balance_rows: int
    issue_count: int
    backup_path: str | None = None


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
            (batch_id, utc_now(), len(income_rows) + len(balance_rows)),
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
            (utc_now(), counts["income"] + counts["balance"], counts["issues"], batch_id),
        )
    return MigrationResult(
        companies=counts["companies"],
        income_rows=counts["income"],
        balance_rows=counts["balance"],
        issue_count=counts["issues"],
        backup_path=str(resolved_backup) if resolved_backup else None,
    )


def verify_database(database_path: str | Path) -> dict[str, int | bool]:
    with sqlite3.connect(Path(database_path).resolve()) as connection:
        return {
            "companies": connection.execute("SELECT COUNT(*) FROM companies").fetchone()[0],
            "income_statements": connection.execute("SELECT COUNT(*) FROM income_statements").fetchone()[0],
            "balance_sheets": connection.execute("SELECT COUNT(*) FROM balance_sheets").fetchone()[0],
            "negative_financial_expenses": connection.execute("SELECT COUNT(*) FROM income_statements WHERE financial_expenses < 0").fetchone()[0],
            "duplicate_income_periods": connection.execute("SELECT COUNT(*) FROM (SELECT code, report_period FROM income_statements GROUP BY code, report_period HAVING COUNT(*) > 1)").fetchone()[0],
            "duplicate_balance_periods": connection.execute("SELECT COUNT(*) FROM (SELECT code, report_period FROM balance_sheets GROUP BY code, report_period HAVING COUNT(*) > 1)").fetchone()[0],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="迁移并验证标准化财务数据")
    parser.add_argument("--database", required=True)
    parser.add_argument("--backup")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        print(verify_database(args.database))
        return
    result = migrate_database(args.database, args.backup)
    print(
        f"companies={result.companies}, income_statements={result.income_rows}, "
        f"balance_sheets={result.balance_rows}, issues={result.issue_count}"
    )


if __name__ == "__main__":
    main()

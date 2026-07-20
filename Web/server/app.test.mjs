import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { DatabaseSync } from 'node:sqlite'
import request from 'supertest'
import { afterEach, describe, expect, it } from 'vitest'

import { createApp } from './app.mjs'

const temporaryDirectories = []

function buildFixtureDatabase() {
  const directory = mkdtempSync(join(tmpdir(), 'financial-web-'))
  temporaryDirectories.push(directory)
  const databasePath = join(directory, 'fixture.db')
  const db = new DatabaseSync(databasePath)
  db.exec(`
    PRAGMA user_version = 1;
    CREATE TABLE companies(code TEXT PRIMARY KEY, name TEXT, market TEXT, raw_code TEXT, industry_name TEXT, updated_at TEXT);
    CREATE TABLE income_statements(id INTEGER PRIMARY KEY, code TEXT, report_period TEXT, report_type TEXT, total_operating_income INTEGER, net_profit INTEGER, net_profit_attributable_to_parent INTEGER, gross_profit INTEGER, gross_profit_margin REAL, revenue_yoy_growth REAL, financial_expenses INTEGER, operating_cost INTEGER, sales_expenses INTEGER, management_expenses INTEGER, research_and_development_expenses INTEGER, business_tax_and_surcharges INTEGER, operating_profit INTEGER, total_profit INTEGER, collected_at TEXT);
    CREATE TABLE balance_sheets(id INTEGER PRIMARY KEY, code TEXT, report_period TEXT, report_type TEXT, total_assets INTEGER, total_liabilities INTEGER, accounts_receivable INTEGER, paid_in_capital INTEGER, capital_reserve INTEGER, undistributed_profits INTEGER, minority_shareholder_equity INTEGER, collected_at TEXT);
    CREATE TABLE import_batches(batch_id TEXT PRIMARY KEY, source_name TEXT, started_at TEXT, completed_at TEXT, status TEXT, raw_row_count INTEGER, normalized_row_count INTEGER, issue_count INTEGER);
    CREATE TABLE data_quality_issues(id INTEGER PRIMARY KEY, batch_id TEXT, statement_type TEXT, code TEXT, report_period TEXT, field_name TEXT, raw_value TEXT, issue_code TEXT, issue_message TEXT, created_at TEXT);
    INSERT INTO companies VALUES ('SH600998', '九州通', 'SH', '600998', NULL, '2026-07-20T00:00:00Z');
    INSERT INTO income_statements VALUES (1, 'SH600998', '2025-12-31', 'FY', 1000, 100, 95, 200, 20, 8, -5, 800, 40, 30, 20, 10, 120, 115, '2026-01-01T00:00:00Z');
    INSERT INTO balance_sheets VALUES (1, 'SH600998', '2025-12-31', 'FY', 2000, 1200, 300, 100, 80, 250, 20, '2026-01-01T00:00:00Z');
  `)
  db.close()
  return databasePath
}

afterEach(() => {
  while (temporaryDirectories.length) rmSync(temporaryDirectories.pop(), { recursive: true, force: true })
})

describe('数据库健康接口', () => {
  it('返回真实数据库状态与元数据', async () => {
    const databasePath = buildFixtureDatabase()
    const app = createApp({ databasePath })
    const health = await request(app).get('/api/health').expect(200)
    expect(health.body).toMatchObject({ status: 'ok', schemaVersion: 1 })
    const meta = await request(app).get('/api/meta').expect(200)
    expect(meta.body).toMatchObject({ databasePath, companyCount: 1, incomeStatementCount: 1 })
  })

  it('数据库不存在时返回稳定错误且不使用模拟数据', async () => {
    const app = createApp({ databasePath: join(tmpdir(), 'definitely-missing-financial.db') })
    const response = await request(app).get('/api/health').expect(503)
    expect(response.body.error).toMatchObject({ code: 'DATABASE_NOT_FOUND', retryable: true, scope: 'application' })
  })
})

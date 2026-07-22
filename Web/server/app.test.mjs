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
    PRAGMA user_version = 2;
    CREATE TABLE companies(code TEXT PRIMARY KEY, name TEXT, market TEXT, raw_code TEXT, industry_name TEXT, business_model TEXT, updated_at TEXT);
    CREATE TABLE income_statements(id INTEGER PRIMARY KEY, code TEXT, report_period TEXT, report_type TEXT, total_operating_income INTEGER, net_profit INTEGER, net_profit_attributable_to_parent INTEGER, net_profit_after_non_recurring INTEGER, gross_profit INTEGER, gross_profit_margin REAL, revenue_yoy_growth REAL, financial_expenses INTEGER, interest_expenses INTEGER, operating_cost INTEGER, sales_expenses INTEGER, management_expenses INTEGER, research_and_development_expenses INTEGER, business_tax_and_surcharges INTEGER, operating_profit INTEGER, total_profit INTEGER, collected_at TEXT);
    CREATE TABLE balance_sheets(id INTEGER PRIMARY KEY, code TEXT, report_period TEXT, report_type TEXT, total_assets INTEGER, total_liabilities INTEGER, accounts_receivable INTEGER, inventory INTEGER, accounts_payable INTEGER, monetary_funds INTEGER, current_assets INTEGER, current_liabilities INTEGER, short_term_borrowings INTEGER, long_term_borrowings INTEGER, total_equity INTEGER, equity_attributable_to_parent INTEGER, goodwill INTEGER, paid_in_capital INTEGER, capital_reserve INTEGER, undistributed_profits INTEGER, minority_shareholder_equity INTEGER, collected_at TEXT);
    CREATE TABLE cash_flow_statements(id INTEGER PRIMARY KEY, code TEXT, report_period TEXT, report_type TEXT, net_operating_cash_flow INTEGER, net_investing_cash_flow INTEGER, net_financing_cash_flow INTEGER, cash_received_from_sales INTEGER, capital_expenditure INTEGER, ending_cash_and_equivalents INTEGER, collected_at TEXT);
    CREATE TABLE import_batches(batch_id TEXT PRIMARY KEY, source_name TEXT, started_at TEXT, completed_at TEXT, status TEXT, raw_row_count INTEGER, normalized_row_count INTEGER, issue_count INTEGER);
    CREATE TABLE data_quality_issues(id INTEGER PRIMARY KEY, batch_id TEXT, statement_type TEXT, code TEXT, report_period TEXT, field_name TEXT, raw_value TEXT, issue_code TEXT, issue_message TEXT, created_at TEXT);
    INSERT INTO companies VALUES ('SH600998', '九州通', 'SH', '600998', NULL, NULL, '2026-07-20T00:00:00Z');
    INSERT INTO income_statements VALUES (1, 'SH600998', '2025-12-31', 'FY', 1000, 100, 95, 90, 200, 20, 8, -5, 5, 800, 40, 30, 20, 10, 120, 115, '2026-01-01T00:00:00Z');
    INSERT INTO balance_sheets VALUES (1, 'SH600998', '2025-12-31', 'FY', 2000, 1200, 300, 180, 150, 200, 800, 500, 100, 200, 800, 700, 10, 100, 80, 250, 20, '2026-01-01T00:00:00Z');
    INSERT INTO cash_flow_statements VALUES (1, 'SH600998', '2025-12-31', 'FY', 100, -30, 10, 900, 30, 200, '2026-01-01T00:00:00Z');
    INSERT INTO companies VALUES ('SH600056', '中国医药', 'SH', '600056', NULL, NULL, '2026-07-20T00:00:00Z');
    INSERT INTO income_statements
      (id, code, report_period, report_type, total_operating_income, net_profit_attributable_to_parent, gross_profit, operating_cost, operating_profit, total_profit, collected_at)
      VALUES
      (2, 'SH600998', '2025-09-30', 'Q3', 700, 60, 140, 560, 80, 75, '2026-01-01T00:00:00Z'),
      (3, 'SH600056', '2025-12-31', 'FY', 800, 70, 160, 640, 90, 85, '2026-01-01T00:00:00Z'),
      (4, 'SH600056', '2025-09-30', 'Q3', 550, 45, 110, 440, 60, 55, '2026-01-01T00:00:00Z');
    INSERT INTO balance_sheets
      (id, code, report_period, report_type, total_assets, total_liabilities, accounts_receivable, inventory, accounts_payable, equity_attributable_to_parent, collected_at)
      VALUES
      (2, 'SH600998', '2025-09-30', 'Q3', 1900, 1150, 280, 170, 140, 680, '2026-01-01T00:00:00Z'),
      (3, 'SH600056', '2025-12-31', 'FY', 1600, 900, 220, 150, 130, 650, '2026-01-01T00:00:00Z'),
      (4, 'SH600056', '2025-09-30', 'Q3', 1500, 850, 210, 145, 125, 620, '2026-01-01T00:00:00Z');
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
    expect(health.body).toMatchObject({ status: 'ok', schemaVersion: 2 })
    const meta = await request(app).get('/api/meta').expect(200)
    expect(meta.body).toMatchObject({ databasePath, companyCount: 2, incomeStatementCount: 4, cashFlowStatementCount: 1 })
  })

  it('数据库不存在时返回稳定错误且不使用模拟数据', async () => {
    const app = createApp({ databasePath: join(tmpdir(), 'definitely-missing-financial.db') })
    const response = await request(app).get('/api/health').expect(503)
    expect(response.body.error).toMatchObject({ code: 'DATABASE_NOT_FOUND', retryable: true, scope: 'application' })
  })

  it('同行接口返回共同报告期并在旧期间失效时回退最新期间', async () => {
    const databasePath = buildFixtureDatabase()
    const app = createApp({ databasePath })
    const selected = await request(app)
      .get('/api/compare?codes=SH600998,SH600056&mode=absolute&period=2025-09-30')
      .expect(200)
    expect(selected.body).toMatchObject({
      availablePeriods: ['2025-12-31', '2025-09-30'],
      commonPeriod: '2025-09-30',
      sampleSize: 2,
    })

    const fallback = await request(app)
      .get('/api/compare?codes=SH600998,SH600056&mode=absolute&period=2024-12-31')
      .expect(200)
    expect(fallback.body).toMatchObject({
      availablePeriods: ['2025-12-31', '2025-09-30'],
      commonPeriod: '2025-12-31',
    })
  })

  it('公司分析接口返回标准现金流及现金质量指标', async () => {
    const databasePath = buildFixtureDatabase()
    const app = createApp({ databasePath })
    const response = await request(app).get('/api/companies/SH600998/analysis').expect(200)
    const annual = response.body.records.find((row) => row.reportPeriod === '2025-12-31')

    expect(response.body.company.cashFlowAvailable).toBe(true)
    expect(response.body.cashFlowNotice).toBeNull()
    expect(annual.cashFlow).toMatchObject({
      netOperatingCashFlow: 100,
      netInvestingCashFlow: -30,
      netFinancingCashFlow: 10,
      cashReceivedFromSales: 900,
      capitalExpenditure: 30,
      endingCashAndEquivalents: 200,
    })
    expect(annual.ratios).toMatchObject({ cashRevenueRatio: 90, freeCashFlow: 70 })
    expect(annual.ratios.cashProfitRatio).toBeCloseTo(100 / 95)
  })
})

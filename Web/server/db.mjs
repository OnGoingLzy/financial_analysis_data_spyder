import { existsSync, statSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { DatabaseSync } from 'node:sqlite'

import { ApiError } from './errors.mjs'
import { calculatePeerMetrics, calculateRatios, findLatestCommonPeriod, median, openingBalancePeriod, percentileRank } from './metrics.mjs'

export const DEFAULT_DATABASE_PATH = import.meta.url.startsWith('file:')
  ? resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', 'financial_analysis.db')
  : resolve(process.cwd(), '..', 'financial_analysis.db')
const requiredTables = ['companies', 'income_statements', 'balance_sheets', 'cash_flow_statements', 'import_batches', 'data_quality_issues']

export function openDatabase(databasePath = DEFAULT_DATABASE_PATH) {
  if (!existsSync(databasePath)) {
    throw new ApiError('DATABASE_NOT_FOUND', '未找到财务数据库', 503, true)
  }
  let db
  try {
    db = new DatabaseSync(databasePath, { readOnly: true })
    const version = db.prepare('PRAGMA user_version').get().user_version
    const tables = new Set(db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all().map((row) => row.name))
    if (version < 1 || requiredTables.some((table) => !tables.has(table))) {
      db.close()
      throw new ApiError('DATABASE_SCHEMA_INVALID', '数据库尚未完成标准化迁移', 503, false)
    }
    return db
  } catch (error) {
    if (error instanceof ApiError) throw error
    if (db?.isOpen) db.close()
    throw new ApiError('DATABASE_UNAVAILABLE', '财务数据库暂时不可读', 503, true)
  }
}

function one(db, sql, params = {}) {
  return db.prepare(sql).get(params)
}

function all(db, sql, params = {}) {
  return db.prepare(sql).all(params)
}

function incomeToCamel(row) {
  if (!row) return null
  return {
    reportPeriod: row.report_period,
    reportType: row.report_type,
    revenue: row.total_operating_income,
    totalOperatingCost: row.total_operating_cost,
    operatingCost: row.operating_cost,
    grossProfit: row.gross_profit,
    grossMargin: row.gross_profit_margin,
    netProfit: row.net_profit,
    netProfitToParent: row.net_profit_attributable_to_parent,
    revenueYoyGrowth: row.revenue_yoy_growth,
    financialExpenses: row.financial_expenses,
    salesExpenses: row.sales_expenses,
    managementExpenses: row.management_expenses,
    researchExpenses: row.research_and_development_expenses,
    taxesAndSurcharges: row.business_tax_and_surcharges,
    operatingProfit: row.operating_profit,
    totalProfit: row.total_profit,
    interestExpenses: row.interest_expenses,
    netProfitAfterNonRecurring: row.net_profit_after_non_recurring,
  }
}

function balanceToCamel(row) {
  if (!row) return null
  const equityToParent = row.equity_attributable_to_parent ?? (row.total_assets == null || row.total_liabilities == null
    ? null
    : row.total_assets - row.total_liabilities - (row.minority_shareholder_equity ?? 0))
  return {
    reportPeriod: row.report_period,
    reportType: row.report_type,
    totalAssets: row.total_assets,
    totalLiabilities: row.total_liabilities,
    accountsReceivable: row.accounts_receivable,
    paidInCapital: row.paid_in_capital,
    capitalReserve: row.capital_reserve,
    undistributedProfits: row.undistributed_profits,
    minorityShareholderEquity: row.minority_shareholder_equity,
    equityToParent,
    monetaryFunds: row.monetary_funds,
    inventory: row.inventory,
    accountsPayable: row.accounts_payable,
    currentAssets: row.current_assets,
    currentLiabilities: row.current_liabilities,
    shortTermBorrowings: row.short_term_borrowings,
    longTermBorrowings: row.long_term_borrowings,
    totalEquity: row.total_equity,
    goodwill: row.goodwill,
  }
}

function cashFlowToCamel(row) {
  if (!row) return null
  return {
    reportPeriod: row.report_period,
    reportType: row.report_type,
    netOperatingCashFlow: row.net_operating_cash_flow,
    netInvestingCashFlow: row.net_investing_cash_flow,
    netFinancingCashFlow: row.net_financing_cash_flow,
    cashReceivedFromSales: row.cash_received_from_sales,
    capitalExpenditure: row.capital_expenditure,
    endingCashAndEquivalents: row.ending_cash_and_equivalents,
  }
}

export function getMeta(db, databasePath) {
  const income = one(db, 'SELECT COUNT(*) count, MIN(report_period) minPeriod, MAX(report_period) maxPeriod FROM income_statements')
  return {
    schemaVersion: one(db, 'PRAGMA user_version').user_version,
    databasePath,
    modifiedAt: statSync(databasePath).mtime.toISOString(),
    companyCount: one(db, 'SELECT COUNT(*) count FROM companies').count,
    periodStart: income.minPeriod,
    periodEnd: income.maxPeriod,
    incomeStatementCount: income.count,
    balanceSheetCount: one(db, 'SELECT COUNT(*) count FROM balance_sheets').count,
    cashFlowStatementCount: one(db, 'SELECT COUNT(*) count FROM cash_flow_statements').count,
    qualityIssueCount: one(db, 'SELECT COUNT(*) count FROM data_quality_issues').count,
  }
}

export function getPeriods(db) {
  return all(db, 'SELECT DISTINCT report_period reportPeriod, report_type reportType FROM income_statements ORDER BY report_period DESC')
}

export function getCompanies(db, search = '') {
  return all(
    db,
    `SELECT code, name, market, industry_name industryName,
       (SELECT MAX(report_period) FROM income_statements i WHERE i.code=c.code) latestPeriod
     FROM companies c WHERE name LIKE :search OR code LIKE :search ORDER BY code`,
    { search: `%${search}%` },
  )
}

export function getCompany(db, code) {
  const company = one(db, 'SELECT code, name, market, industry_name industryName FROM companies WHERE code=:code', { code })
  if (!company) throw new ApiError('COMPANY_NOT_FOUND', '未找到该公司', 404, false, 'company')
  const periods = all(db, 'SELECT report_period reportPeriod, report_type reportType FROM income_statements WHERE code=:code ORDER BY report_period DESC', { code })
  const cashFlowAvailable = one(db, 'SELECT COUNT(*) count FROM cash_flow_statements WHERE code=:code', { code }).count > 0
  return { ...company, periods, cashFlowAvailable }
}

function getAnalysisRows(db, code) {
  const income = all(db, 'SELECT * FROM income_statements WHERE code=:code ORDER BY report_period', { code }).map(incomeToCamel)
  const balances = all(db, 'SELECT * FROM balance_sheets WHERE code=:code ORDER BY report_period', { code }).map(balanceToCamel)
  const cashFlows = all(db, 'SELECT * FROM cash_flow_statements WHERE code=:code ORDER BY report_period', { code }).map(cashFlowToCamel)
  const balanceMap = new Map(balances.map((row) => [row.reportPeriod, row]))
  const cashFlowMap = new Map(cashFlows.map((row) => [row.reportPeriod, row]))
  return income.map((row) => {
    const balance = balanceMap.get(row.reportPeriod) ?? null
    const previousPeriod = openingBalancePeriod(row.reportPeriod)
    const previousBalance = previousPeriod ? balanceMap.get(previousPeriod) ?? null : null
    const cashFlow = cashFlowMap.get(row.reportPeriod) ?? null
    return { ...row, balance, cashFlow, ratios: balance ? calculatePeerMetrics(row, balance, previousBalance, cashFlow) : null }
  })
}

export function getCompanyAnalysis(db, code) {
  const company = getCompany(db, code)
  return { company, records: getAnalysisRows(db, code), cashFlowNotice: company.cashFlowAvailable ? null : '当前公司尚未补采现金流量表，现金分析保持为空。' }
}

export function getComparison(db, codes, requestedPeriod, mode = 'absolute') {
  const periodsByCompany = codes.map((code) => all(db, 'SELECT report_period reportPeriod FROM income_statements WHERE code=:code', { code }).map((row) => row.reportPeriod))
  const commonPeriod = requestedPeriod || findLatestCommonPeriod(periodsByCompany)
  if (!commonPeriod) throw new ApiError('NO_COMMON_PERIOD', '所选公司没有共同报告期', 422, false, 'comparison')
  const rows = codes.map((code) => {
    const company = one(db, 'SELECT code, name FROM companies WHERE code=:code', { code })
    if (!company) throw new ApiError('COMPANY_NOT_FOUND', `未找到公司 ${code}`, 404, false, 'comparison')
    const income = incomeToCamel(one(db, 'SELECT * FROM income_statements WHERE code=:code AND report_period=:period', { code, period: commonPeriod }))
    const balance = balanceToCamel(one(db, 'SELECT * FROM balance_sheets WHERE code=:code AND report_period=:period', { code, period: commonPeriod }))
    const previousPeriod = openingBalancePeriod(commonPeriod)
    const previousBalance = balanceToCamel(one(db, 'SELECT * FROM balance_sheets WHERE code=:code AND report_period=:period', { code, period: previousPeriod }))
    const cashFlow = cashFlowToCamel(one(db, 'SELECT * FROM cash_flow_statements WHERE code=:code AND report_period=:period', { code, period: commonPeriod }))
    const peerMetrics = income && balance ? calculatePeerMetrics(income, balance, previousBalance, cashFlow) : {}
    const profile = { ...income, ...peerMetrics }
    return { ...company, profile, metrics: profile }
  })
  const metricNames = ['revenue', 'netProfitToParent', 'grossMargin', 'netMargin', 'operatingMargin', 'debtRatio', 'revenueYoyGrowth', 'cashProfitRatio', 'cashConversionCycle', 'roe', 'assetTurnover', 'currentRatio', 'quickRatio', 'salesExpenseRatio', 'researchExpenseRatio']
  const medians = Object.fromEntries(metricNames.map((name) => [name, median(rows.map((row) => row.metrics?.[name] ?? null))]))
  const normalizedRows = rows.map((row) => ({
    ...row,
    metrics: Object.fromEntries(metricNames.map((name) => {
      const value = row.metrics?.[name] ?? null
      const middle = medians[name]
      const displayValue = mode === 'index' ? (value == null || middle == null || middle === 0 ? null : value / middle * 100) : value
      return [name, { value: displayValue, rawValue: value, percentile: percentileRank(value, rows.map((item) => item.metrics?.[name] ?? null)) }]
    })),
  }))
  return { commonPeriod, mode, sampleSize: rows.length, medians, rows: normalizedRows }
}

export function getDataQuality(db) {
  return {
    batches: all(db, 'SELECT batch_id batchId, source_name sourceName, started_at startedAt, completed_at completedAt, status, raw_row_count rawRowCount, normalized_row_count normalizedRowCount, issue_count issueCount FROM import_batches ORDER BY started_at DESC LIMIT 20'),
    issues: all(db, 'SELECT statement_type statementType, code, report_period reportPeriod, field_name fieldName, raw_value rawValue, issue_code issueCode, issue_message issueMessage, created_at createdAt FROM data_quality_issues ORDER BY id DESC LIMIT 200'),
  }
}

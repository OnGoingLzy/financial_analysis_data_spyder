import { describe, expect, it } from 'vitest'

import { buildCompareQuery, deriveBasisRecords } from './viewModel'

describe('分析视图状态', () => {
  it('同行模式与公司集合写入 URL', () => {
    expect(buildCompareQuery(['SH600998', 'SZ002788'], 'index', '2025-12-31')).toBe(
      'codes=SH600998%2CSZ002788&mode=index&period=2025-12-31',
    )
  })

  it('单公司口径支持累计、单季度、TTM 与年度', () => {
    const records = [
      { reportPeriod: '2025-03-31', reportType: 'Q1', revenue: 10, netProfit: -1 },
      { reportPeriod: '2025-06-30', reportType: 'H1', revenue: 25, netProfit: 2 },
      { reportPeriod: '2025-09-30', reportType: 'Q3', revenue: 45, netProfit: 4 },
      { reportPeriod: '2025-12-31', reportType: 'FY', revenue: 70, netProfit: 8 },
    ]
    expect(deriveBasisRecords(records, 'quarterly').map((row) => row.revenue)).toEqual([10, 15, 20, 25])
    expect(deriveBasisRecords(records, 'ttm').at(-1)?.revenue).toBe(70)
    expect(deriveBasisRecords(records, 'annual')).toHaveLength(1)
    expect(deriveBasisRecords(records, 'cumulative')).toEqual(records)
  })

  it('单季度与 TTM 同步转换现金流并重算现金质量指标', () => {
    const records = [
      { reportPeriod: '2025-03-31', reportType: 'Q1', revenue: 100, netProfitToParent: 10, cashFlow: { netOperatingCashFlow: 12, netInvestingCashFlow: -4, netFinancingCashFlow: 2, cashReceivedFromSales: 105, capitalExpenditure: 3, endingCashAndEquivalents: 50 }, ratios: {} },
      { reportPeriod: '2025-06-30', reportType: 'H1', revenue: 230, netProfitToParent: 25, cashFlow: { netOperatingCashFlow: 30, netInvestingCashFlow: -9, netFinancingCashFlow: 4, cashReceivedFromSales: 240, capitalExpenditure: 8, endingCashAndEquivalents: 56 }, ratios: {} },
      { reportPeriod: '2025-09-30', reportType: 'Q3', revenue: 390, netProfitToParent: 43, cashFlow: { netOperatingCashFlow: 51, netInvestingCashFlow: -15, netFinancingCashFlow: 3, cashReceivedFromSales: 405, capitalExpenditure: 14, endingCashAndEquivalents: 61 }, ratios: {} },
      { reportPeriod: '2025-12-31', reportType: 'FY', revenue: 580, netProfitToParent: 65, cashFlow: { netOperatingCashFlow: 78, netInvestingCashFlow: -24, netFinancingCashFlow: 1, cashReceivedFromSales: 610, capitalExpenditure: 22, endingCashAndEquivalents: 70 }, ratios: {} },
    ]

    const quarterly = deriveBasisRecords(records, 'quarterly')
    expect(quarterly[1].cashFlow).toMatchObject({ netOperatingCashFlow: 18, cashReceivedFromSales: 135, capitalExpenditure: 5, endingCashAndEquivalents: 56 })
    expect(quarterly[1].ratios).toMatchObject({ cashProfitRatio: 1.2, cashRevenueRatio: 135 / 130 * 100, freeCashFlow: 13 })

    const ttm = deriveBasisRecords(records, 'ttm').at(-1)
    expect(ttm?.cashFlow).toMatchObject({ netOperatingCashFlow: 78, netInvestingCashFlow: -24, netFinancingCashFlow: 1, cashReceivedFromSales: 610, capitalExpenditure: 22, endingCashAndEquivalents: 70 })
    expect(ttm?.ratios).toMatchObject({ cashProfitRatio: 78 / 65, cashRevenueRatio: 610 / 580 * 100, freeCashFlow: 56 })
  })
})

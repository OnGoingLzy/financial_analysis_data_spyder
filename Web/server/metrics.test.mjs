import { describe, expect, it } from 'vitest'

import { calculatePeerMetrics, calculateRatios, calculateTtm, deriveSingleQuarters, findCommonPeriods, findLatestCommonPeriod, openingBalancePeriod } from './metrics.mjs'

describe('财务指标引擎', () => {
  const records = [
    { reportPeriod: '2025-03-31', reportType: 'Q1', revenue: 10 },
    { reportPeriod: '2025-06-30', reportType: 'H1', revenue: 25 },
    { reportPeriod: '2025-09-30', reportType: 'Q3', revenue: 45 },
    { reportPeriod: '2025-12-31', reportType: 'FY', revenue: 70 },
  ]

  it('从累计值推导单季度并计算 TTM', () => {
    expect(deriveSingleQuarters(records, 'revenue').map((item) => item.value)).toEqual([10, 15, 20, 25])
    expect(calculateTtm(records, 'revenue')).toBe(70)
  })

  it('相邻累计期缺失时不虚构单季度值', () => {
    const incomplete = [records[0], records[2]]
    expect(deriveSingleQuarters(incomplete, 'revenue').map((item) => item.value)).toEqual([10, null])
    expect(calculateTtm(incomplete, 'revenue')).toBeNull()
  })

  it('共同报告期会回退到所有公司都有数据的最近期间', () => {
    expect(findLatestCommonPeriod([
      ['2025-09-30', '2025-12-31'],
      ['2025-06-30', '2025-09-30'],
    ])).toBe('2025-09-30')
  })

  it('共同报告期返回去重后的倒序交集', () => {
    expect(findCommonPeriods([
      ['2025-09-30', '2025-12-31', '2025-09-30'],
      ['2025-06-30', '2025-09-30', '2025-12-31'],
      ['2025-12-31', '2025-09-30'],
    ])).toEqual(['2025-12-31', '2025-09-30'])
    expect(findCommonPeriods([])).toEqual([])
  })

  it('计算比率并在缺少期初净资产时保持 ROE 为空', () => {
    const ratios = calculateRatios(
      { reportType: 'Q1', revenue: 100, grossProfit: 25, netProfitToParent: -5 },
      { totalAssets: 200, totalLiabilities: 120, equityToParent: 60, accountsReceivable: 30 },
      null,
    )
    expect(ratios).toMatchObject({ grossMargin: 25, netMargin: -5, debtRatio: 60, receivablesToAssets: 15, roe: null })
  })

  it('ROE 的期初净资产固定取上年末', () => {
    expect(openingBalancePeriod('2026-03-31')).toBe('2025-12-31')
    expect(openingBalancePeriod('2025-12-31')).toBe('2024-12-31')
  })
})

describe('同行经营诊断指标', () => {
  it('统一计算费用率、现金质量、周转周期和杜邦分解', () => {
    const metrics = calculatePeerMetrics(
      { reportType: 'FY', revenue: 1000, operatingCost: 700, netProfitToParent: 80, netProfitAfterNonRecurring: 70, salesExpenses: 40, managementExpenses: 30, researchExpenses: 20, financialExpenses: 10, operatingProfit: 110, totalProfit: 100, interestExpenses: 20 },
      { totalAssets: 2000, totalLiabilities: 1200, equityToParent: 700, monetaryFunds: 200, inventory: 180, accountsReceivable: 240, accountsPayable: 150, currentAssets: 800, currentLiabilities: 500, shortTermBorrowings: 100 },
      { totalAssets: 1800, equityToParent: 650, inventory: 160, accountsReceivable: 200, accountsPayable: 130 },
      { netOperatingCashFlow: 100, cashReceivedFromSales: 1100, capitalExpenditure: 30 },
    )
    expect(metrics).toMatchObject({ salesExpenseRatio: 4, operatingMargin: 11, cashProfitRatio: 1.25, freeCashFlow: 70, currentRatio: 1.6, quickRatio: 1.24, cashShortDebtRatio: 2 })
    expect(metrics.cashRevenueRatio).toBeCloseTo(110)
    expect(metrics.cashConversionCycle).toBeCloseTo(95.93, 1)
    expect(metrics.roe).toBeCloseTo(11.85, 1)
    expect(metrics.assetTurnover).toBeCloseTo(0.526, 2)
    expect(metrics.equityMultiplier).toBeCloseTo(2.815, 2)
  })

  it('缺少现金流和期初值时保持 NULL', () => {
    const metrics = calculatePeerMetrics({ reportType: 'FY', revenue: 100, netProfitToParent: 10 }, { totalAssets: 200 }, null, null)
    expect(metrics.cashProfitRatio).toBeNull()
    expect(metrics.cashConversionCycle).toBeNull()
    expect(metrics.roe).toBeNull()
  })
})

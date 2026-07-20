import { describe, expect, it } from 'vitest'

import { calculateRatios, calculateTtm, deriveSingleQuarters, findLatestCommonPeriod, openingBalancePeriod } from './metrics.mjs'

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

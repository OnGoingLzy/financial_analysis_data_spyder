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
})

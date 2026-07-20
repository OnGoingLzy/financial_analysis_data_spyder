import { describe, expect, it } from 'vitest'

import { financialExpenseLabel, formatAmount, formatPercent, metricTone } from './format'

describe('财务数值语义', () => {
  it('使用中国市场红盈绿亏语义', () => {
    expect(metricTone(1, 'profit')).toBe('profit')
    expect(metricTone(-1, 'profit')).toBe('loss')
    expect(metricTone(null, 'profit')).toBe('neutral')
  })

  it('缺失值不伪装成零', () => {
    expect(formatAmount(null)).toBe('暂无数据')
    expect(formatPercent(null)).toBe('暂无数据')
  })

  it('负财务费用解释为财务净收益', () => {
    expect(financialExpenseLabel(-10)).toBe('财务净收益')
    expect(financialExpenseLabel(10)).toBe('财务费用')
  })
})

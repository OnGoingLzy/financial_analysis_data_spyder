import { describe, expect, it } from 'vitest'

import { createBarOption, createTrendOption } from './options'

const colors = {
  accent: '#28d7e5',
  profit: '#ff4d4f',
  loss: '#2bb673',
  muted: '#8da0a8',
  rule: '#26373d',
}

describe('财务图表交互配置', () => {
  it('柱状图悬停时保持图形可见并显示当前金额', () => {
    const option = createBarOption(
      [{ name: '中国医药', value: 34150000000 }],
      '营业收入',
      colors,
    )
    const series = Array.isArray(option.series) ? option.series[0] : option.series
    const formatter = (option.tooltip as { formatter: (params: unknown) => string }).formatter

    expect(series).toMatchObject({
      type: 'bar',
      emphasis: { disabled: true },
      blur: { itemStyle: { opacity: 1 } },
    })
    expect(formatter({ name: '中国医药', value: 34150000000, marker: '●' })).toContain('34,150,000,000 元')
    expect(formatter({ name: '中国医药', value: null, marker: '●' })).toContain('暂无数据')
  })

  it('折线图悬停时不淡化或隐藏任一系列', () => {
    const option = createTrendOption(
      [{ reportPeriod: '2024-12-31', revenue: 10, netProfit: -2 }],
      colors,
    )
    const lines = option.series as Array<{
      emphasis?: { disabled?: boolean }
      blur?: { lineStyle?: { opacity?: number } }
    }>
    expect(lines.every((series) => (
      series.emphasis?.disabled === true
      && series.blur?.lineStyle?.opacity === 1
    ))).toBe(true)
    expect(option.tooltip).toMatchObject({ trigger: 'axis' })
  })
})

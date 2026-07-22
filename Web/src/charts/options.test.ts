import { describe, expect, it } from 'vitest'

import { createBarOption, createCashFlowTrendOption, createCashRiskOption, createGrowthProfitOption, createIncomeStructureOption, createPeerHeatmapOption, createTrendOption, createWorkingCapitalOption } from './options'

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

  it('现金流图展示三类现金流并在悬停时保持柱体可见', () => {
    const option = createCashFlowTrendOption([{
      reportPeriod: '2025-12-31',
      cashFlow: { netOperatingCashFlow: 100, netInvestingCashFlow: -30, netFinancingCashFlow: 10 },
    }], colors)
    const series = option.series as Array<{ name: string; data: unknown[]; itemStyle?: { color?: string }; emphasis?: { disabled?: boolean } }>
    const formatter = (option.tooltip as { formatter: (params: unknown) => string }).formatter

    expect(series.map((item) => item.name)).toEqual(['经营活动现金流', '投资活动现金流', '筹资活动现金流'])
    expect(series.map((item) => item.itemStyle?.color)).toEqual([colors.profit, colors.accent, colors.muted])
    expect(series.every((item) => item.emphasis?.disabled === true)).toBe(true)
    expect(formatter([{ name: '2025-12-31', seriesName: '经营活动现金流', value: 100, marker: '●' }])).toContain('100 元')
  })
})

describe('同行诊断图表配置', () => {
  const rows = [{
    name: '中国医药',
    profile: { revenue: 1000, revenueYoyGrowth: 6, netMargin: 3, operatingCost: 700, salesExpenses: 40, managementExpenses: 30, researchExpenses: 20, financialExpenses: 10, netProfitToParent: 30, receivableDays: 80, inventoryDays: 50, payableDays: 40, cashConversionCycle: 90, cashProfitRatio: 1.2, debtRatio: 60, cashShortDebtRatio: 1.5 },
    metrics: { netMargin: { percentile: 70 }, revenueYoyGrowth: { percentile: 60 }, cashProfitRatio: { percentile: 80 }, cashConversionCycle: { percentile: 40 }, debtRatio: { percentile: 30 } },
  }]

  it('生成五类互补分析图，并保持悬停图形可见', () => {
    expect(createPeerHeatmapOption(rows, colors).series).toBeTruthy()
    expect(createGrowthProfitOption(rows, colors).series).toBeTruthy()
    expect(createIncomeStructureOption(rows, colors).series).toHaveLength(6)
    expect(createWorkingCapitalOption(rows, colors).series).toHaveLength(4)
    expect(createCashRiskOption(rows, colors).series).toBeTruthy()
  })

  it('热力图色阶不向 visualMap 传入无法插值的 OKLCH 颜色', () => {
    const option = createPeerHeatmapOption(rows, {
      ...colors,
      profit: 'oklch(68% 0.2 28)',
      loss: 'oklch(72% 0.15 151)',
      rule: 'oklch(35% 0.022 228)',
    })
    const visualMap = option.visualMap as { inRange: { color: string[] } }
    expect(visualMap.inRange.color).toEqual(['#2bb673', '#26373d', '#ff4d4f'])
  })
})

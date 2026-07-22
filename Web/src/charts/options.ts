import type { EChartsOption } from '@/charts/echarts'

export interface ChartColors {
  accent: string
  profit: string
  loss: string
  muted: string
  rule: string
}

interface BarRow { name: string; value: number | null }
interface TrendRow { reportPeriod: string; revenue: number | null; netProfit: number | null }
interface CashFlowTrendRow { reportPeriod: string; cashFlow: { netOperatingCashFlow?: number | null; netInvestingCashFlow?: number | null; netFinancingCashFlow?: number | null } | null }
interface TooltipDatum { name?: string; seriesName?: string; value?: unknown; marker?: string }

export function readChartColors(): ChartColors {
  const css = getComputedStyle(document.documentElement)
  return {
    accent: css.getPropertyValue('--color-accent').trim(),
    profit: css.getPropertyValue('--color-profit').trim(),
    loss: css.getPropertyValue('--color-loss').trim(),
    muted: css.getPropertyValue('--color-ink-muted').trim(),
    rule: css.getPropertyValue('--color-rule').trim(),
  }
}

function formatRawAmount(value: unknown) {
  return typeof value === 'number' && Number.isFinite(value)
    ? `${value.toLocaleString('zh-CN')} 元`
    : '暂无数据'
}

function tooltipRow(item: TooltipDatum, fallbackName = '') {
  return `${item.marker ?? ''}${item.seriesName ?? fallbackName}　<strong>${formatRawAmount(item.value)}</strong>`
}

function tooltipDatum(value: unknown): TooltipDatum {
  return typeof value === 'object' && value !== null ? value as TooltipDatum : {}
}

export function createBarOption(rows: BarRow[], metricName: string, colors: ChartColors): EChartsOption {
  return {
    animation: false,
    tooltip: {
      trigger: 'item',
      confine: true,
      formatter: (params: unknown) => {
        const item = tooltipDatum(params)
        return `${item.name ?? ''}<br>${tooltipRow(item, metricName)}`
      },
    },
    grid: { left: 96, right: 28, top: 24, bottom: 36, containLabel: true },
    xAxis: { type: 'value', axisLabel: { color: colors.muted }, splitLine: { lineStyle: { color: colors.rule } } },
    yAxis: {
      type: 'category',
      data: rows.map((row) => row.name),
      axisLabel: { color: colors.muted },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [{
      name: metricName,
      type: 'bar',
      data: rows.map((row) => ({
        value: row.value,
        itemStyle: { color: row.value != null && row.value < 0 ? colors.loss : colors.profit },
      })),
      barMaxWidth: 18,
      emphasis: { disabled: true },
      blur: { itemStyle: { opacity: 1 } },
    }],
  }
}

export function createTrendOption(records: TrendRow[], colors: ChartColors): EChartsOption {
  const stableLineState = {
    emphasis: { disabled: true },
    blur: { lineStyle: { opacity: 1 }, itemStyle: { opacity: 1 } },
  }
  return {
    animation: false,
    tooltip: {
      trigger: 'axis',
      confine: true,
      axisPointer: { type: 'line' },
      formatter: (params: unknown) => {
        const items = (Array.isArray(params) ? params : [params]).map(tooltipDatum)
        return `${items[0]?.name ?? ''}<br>${items.map((item) => tooltipRow(item)).join('<br>')}`
      },
    },
    legend: { data: ['营业收入', '净利润'], textStyle: { color: colors.muted } },
    grid: { left: 72, right: 28, top: 48, bottom: 44, containLabel: true },
    xAxis: {
      type: 'category',
      data: records.map((row) => row.reportPeriod),
      axisLabel: { color: colors.muted, rotate: records.length > 8 ? 30 : 0 },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: colors.muted, formatter: (value: number) => `${(value / 100000000).toFixed(0)}亿` },
      splitLine: { lineStyle: { color: colors.rule } },
    },
    series: [
      {
        name: '营业收入', type: 'line', data: records.map((row) => row.revenue), showSymbol: false,
        lineStyle: { color: colors.accent, opacity: 1 }, itemStyle: { color: colors.accent, opacity: 1 },
        ...stableLineState,
      },
      {
        name: '净利润', type: 'line', data: records.map((row) => row.netProfit), showSymbol: false,
        lineStyle: { color: colors.profit, opacity: 1 }, itemStyle: { color: colors.profit, opacity: 1 },
        ...stableLineState,
      },
    ],
  }
}

export function createCashFlowTrendOption(records: CashFlowTrendRow[], colors: ChartColors): EChartsOption {
  const stableBarState = { emphasis: { disabled: true }, blur: { itemStyle: { opacity: 1 } } }
  const definitions = [
    ['netOperatingCashFlow', '经营活动现金流', colors.profit],
    ['netInvestingCashFlow', '投资活动现金流', colors.accent],
    ['netFinancingCashFlow', '筹资活动现金流', colors.muted],
  ] as const
  return {
    animation: false,
    tooltip: {
      trigger: 'axis',
      confine: true,
      axisPointer: { type: 'shadow' },
      formatter: (params: unknown) => {
        const items = (Array.isArray(params) ? params : [params]).map(tooltipDatum)
        return `${items[0]?.name ?? ''}<br>${items.map((item) => tooltipRow(item)).join('<br>')}`
      },
    },
    legend: { data: definitions.map((item) => item[1]), textStyle: { color: colors.muted } },
    grid: { left: 72, right: 28, top: 48, bottom: 44, containLabel: true },
    xAxis: { type: 'category', data: records.map((row) => row.reportPeriod), axisLabel: { color: colors.muted, rotate: records.length > 8 ? 30 : 0 } },
    yAxis: {
      type: 'value',
      axisLabel: { color: colors.muted, formatter: (value: number) => `${(value / 100000000).toFixed(0)}亿` },
      splitLine: { lineStyle: { color: colors.rule } },
    },
    series: definitions.map(([key, name, color]) => ({
      name,
      type: 'bar',
      itemStyle: { color },
      data: records.map((row) => {
        const value = row.cashFlow?.[key] ?? null
        return key === 'netOperatingCashFlow'
          ? { value, itemStyle: { color: value != null && value < 0 ? colors.loss : colors.profit } }
          : { value, itemStyle: { color } }
      }),
      barMaxWidth: 20,
      ...stableBarState,
    })),
  }
}

type PeerRow = {
  name: string
  profile: Record<string, number | null | undefined>
  metrics: Record<string, { percentile?: number | null } | undefined>
}

const stableSeriesState = { emphasis: { disabled: true }, blur: { itemStyle: { opacity: 1 } } }
// zrender 的 visualMap 插值暂不支持 OKLCH，使用与设计令牌对应的 RGB 色值。
const heatmapColorScale = ['#2bb673', '#26373d', '#ff4d4f']

export function createPeerHeatmapOption(rows: PeerRow[], colors: ChartColors): EChartsOption {
  const dimensions = [
    ['netMargin', '净利率', false], ['revenueYoyGrowth', '营收增长', false],
    ['cashProfitRatio', '现金质量', false], ['cashConversionCycle', '现金周期', true],
    ['debtRatio', '负债风险', true],
  ] as const
  const data = rows.flatMap((row, y) => dimensions.map(([key, _label, inverse], x) => {
    const percentile = row.metrics[key]?.percentile ?? null
    return [x, y, percentile == null ? null : inverse ? 100 - percentile : percentile]
  }))
  return {
    animation: false,
    tooltip: { trigger: 'item', confine: true, formatter: (params: unknown) => {
      const item = tooltipDatum(params) as TooltipDatum & { data?: [number, number, number | null] }
      const value = item.data?.[2]
      return `${item.name ?? ''}<br>同行质量分位　<strong>${value == null ? '暂无数据' : `P${Math.round(value)}`}</strong>`
    } },
    grid: { left: 112, right: 28, top: 28, bottom: 48, containLabel: true },
    xAxis: { type: 'category', data: dimensions.map((item) => item[1]), axisLabel: { color: colors.muted } },
    yAxis: { type: 'category', data: rows.map((row) => row.name), axisLabel: { color: colors.muted } },
    visualMap: { min: 0, max: 100, show: false, inRange: { color: heatmapColorScale } },
    series: [{ type: 'heatmap', data, label: { show: true, formatter: (params: unknown) => {
      const item = tooltipDatum(params) as TooltipDatum & { data?: [number, number, number | null] }
      return item.data?.[2] == null ? '—' : `${Math.round(item.data[2])}`
    } }, ...stableSeriesState }],
  }
}

export function createGrowthProfitOption(rows: PeerRow[], colors: ChartColors): EChartsOption {
  return {
    animation: false,
    tooltip: { trigger: 'item', confine: true, formatter: (params: unknown) => {
      const item = tooltipDatum(params) as TooltipDatum & { data?: { name: string; value: number[] } }
      const value = item.data?.value ?? []
      return `${item.data?.name ?? ''}<br>营收同比　${value[0]?.toFixed(2) ?? '—'}%<br>净利率　${value[1]?.toFixed(2) ?? '—'}%`
    } },
    grid: { left: 56, right: 28, top: 28, bottom: 48, containLabel: true },
    xAxis: { type: 'value', name: '营收同比 %', axisLabel: { color: colors.muted }, splitLine: { lineStyle: { color: colors.rule } } },
    yAxis: { type: 'value', name: '净利率 %', axisLabel: { color: colors.muted }, splitLine: { lineStyle: { color: colors.rule } } },
    series: [{ type: 'scatter', data: rows.filter((row) => row.profile.revenueYoyGrowth != null && row.profile.netMargin != null).map((row) => ({ name: row.name, value: [row.profile.revenueYoyGrowth, row.profile.netMargin, row.profile.revenue], itemStyle: { color: (row.profile.netMargin ?? 0) < 0 ? colors.loss : colors.profit } })), symbolSize: (value: number[]) => Math.max(12, Math.min(42, Math.sqrt(Math.abs(value[2] ?? 0)) / 5000)), ...stableSeriesState }],
  }
}

export function createIncomeStructureOption(rows: PeerRow[], colors: ChartColors): EChartsOption {
  const definitions = [
    ['operatingCost', '营业成本', colors.muted], ['salesExpenses', '销售费用', colors.accent],
    ['managementExpenses', '管理费用', colors.rule], ['researchExpenses', '研发费用', colors.accent],
    ['financialExpenses', '财务费用', colors.loss], ['netProfitToParent', '归母净利润', colors.profit],
  ] as const
  return {
    animation: false, tooltip: { trigger: 'axis', confine: true }, legend: { textStyle: { color: colors.muted } },
    grid: { left: 96, right: 28, top: 56, bottom: 40, containLabel: true },
    xAxis: { type: 'value', axisLabel: { color: colors.muted, formatter: '{value}%' }, splitLine: { lineStyle: { color: colors.rule } } },
    yAxis: { type: 'category', data: rows.map((row) => row.name), axisLabel: { color: colors.muted } },
    series: definitions.map(([key, name, color]) => ({ name, type: 'bar', stack: '收入', data: rows.map((row) => row.profile.revenue ? (row.profile[key] ?? 0) / row.profile.revenue * 100 : null), itemStyle: { color }, ...stableSeriesState })),
  }
}

export function createWorkingCapitalOption(rows: PeerRow[], colors: ChartColors): EChartsOption {
  const definitions = [['receivableDays', '应收天数', colors.accent], ['inventoryDays', '存货天数', colors.profit], ['payableDays', '应付天数', colors.muted], ['cashConversionCycle', '现金周期', colors.loss]] as const
  return {
    animation: false, tooltip: { trigger: 'axis', confine: true }, legend: { textStyle: { color: colors.muted } },
    grid: { left: 96, right: 28, top: 56, bottom: 40, containLabel: true },
    xAxis: { type: 'value', axisLabel: { color: colors.muted, formatter: '{value}天' }, splitLine: { lineStyle: { color: colors.rule } } },
    yAxis: { type: 'category', data: rows.map((row) => row.name), axisLabel: { color: colors.muted } },
    series: definitions.map(([key, name, color]) => ({ name, type: 'bar', data: rows.map((row) => row.profile[key]), itemStyle: { color }, ...stableSeriesState })),
  }
}

export function createCashRiskOption(rows: PeerRow[], colors: ChartColors): EChartsOption {
  return {
    animation: false, tooltip: { trigger: 'item', confine: true },
    grid: { left: 56, right: 28, top: 28, bottom: 48, containLabel: true },
    xAxis: { type: 'value', name: '资产负债率 %', axisLabel: { color: colors.muted }, splitLine: { lineStyle: { color: colors.rule } } },
    yAxis: { type: 'value', name: '经营现金流/净利润', axisLabel: { color: colors.muted }, splitLine: { lineStyle: { color: colors.rule } } },
    series: [{ type: 'scatter', data: rows.filter((row) => row.profile.debtRatio != null && row.profile.cashProfitRatio != null).map((row) => ({ name: row.name, value: [row.profile.debtRatio, row.profile.cashProfitRatio, row.profile.cashShortDebtRatio], itemStyle: { color: (row.profile.cashProfitRatio ?? 0) < 1 ? colors.loss : colors.profit } })), symbolSize: 18, ...stableSeriesState }],
  }
}

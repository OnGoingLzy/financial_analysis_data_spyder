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

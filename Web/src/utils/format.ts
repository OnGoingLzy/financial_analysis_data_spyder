export type MetricKind = 'profit' | 'growth' | 'neutral'

export function metricTone(value: number | null | undefined, kind: MetricKind = 'profit') {
  if (value == null || kind === 'neutral' || value === 0) return 'neutral'
  return value > 0 ? 'profit' : 'loss'
}

export function formatAmount(value: number | null | undefined) {
  if (value == null) return '暂无数据'
  const absolute = Math.abs(value)
  const sign = value > 0 ? '+' : value < 0 ? '−' : ''
  if (absolute >= 100_000_000) return `${sign}${(absolute / 100_000_000).toFixed(2)}亿`
  if (absolute >= 10_000) return `${sign}${(absolute / 10_000).toFixed(2)}万`
  return `${sign}${absolute.toLocaleString('zh-CN')}元`
}

export function formatPercent(value: number | null | undefined) {
  if (value == null) return '暂无数据'
  const sign = value > 0 ? '+' : value < 0 ? '−' : ''
  return `${sign}${Math.abs(value).toFixed(2)}%`
}

export function formatNumber(value: number | null | undefined) {
  if (value == null) return '暂无数据'
  return value.toFixed(1)
}

export function financialExpenseLabel(value: number | null | undefined) {
  return value != null && value < 0 ? '财务净收益' : '财务费用'
}

export function reportTypeLabel(type: string) {
  return ({ Q1: '一季报', H1: '半年报', Q3: '三季报', FY: '年报' } as Record<string, string>)[type] ?? type
}

export type Basis = 'cumulative' | 'quarterly' | 'ttm' | 'annual'
type RecordValue = { reportPeriod: string; reportType: string; [key: string]: unknown }
const numericFields = ['revenue', 'netProfit', 'netProfitToParent', 'grossProfit', 'operatingProfit', 'financialExpenses', 'salesExpenses', 'managementExpenses', 'researchExpenses']
const cashFlowFields = ['netOperatingCashFlow', 'netInvestingCashFlow', 'netFinancingCashFlow', 'cashReceivedFromSales', 'capitalExpenditure']

function readObject(value: unknown): Record<string, unknown> | null {
  return typeof value === 'object' && value !== null ? value as Record<string, unknown> : null
}

function divide(numerator: unknown, denominator: unknown, percent = false) {
  if (typeof numerator !== 'number' || typeof denominator !== 'number' || denominator === 0) return null
  return numerator / denominator * (percent ? 100 : 1)
}

function refreshCashRatios(output: Record<string, unknown>) {
  const cashFlow = readObject(output.cashFlow)
  const ratios = { ...(readObject(output.ratios) ?? {}) }
  const netProfit = typeof output.netProfitToParent === 'number' ? output.netProfitToParent : output.netProfit
  ratios.cashProfitRatio = divide(cashFlow?.netOperatingCashFlow, netProfit)
  ratios.cashRevenueRatio = divide(cashFlow?.cashReceivedFromSales, output.revenue, true)
  ratios.freeCashFlow = typeof cashFlow?.netOperatingCashFlow === 'number' && typeof cashFlow.capitalExpenditure === 'number'
    ? cashFlow.netOperatingCashFlow - cashFlow.capitalExpenditure
    : null
  output.ratios = ratios
}

export function buildCompareQuery(codes: string[], mode: string, period?: string | null) {
  const params = new URLSearchParams({ codes: codes.join(','), mode })
  if (period) params.set('period', period)
  return params.toString()
}

export function deriveBasisRecords<T extends RecordValue>(records: T[], basis: Basis): T[] {
  if (basis === 'cumulative') return records
  if (basis === 'annual') return records.filter((row) => row.reportType === 'FY')
  const quarterly = records.map((row, index) => {
    if (row.reportType === 'Q1') return { ...row }
    const previous = records[index - 1]
    const expected = row.reportType === 'H1' ? 'Q1' : row.reportType === 'Q3' ? 'H1' : 'Q3'
    const sameYear = previous?.reportPeriod.slice(0, 4) === row.reportPeriod.slice(0, 4)
    const output: Record<string, unknown> = { ...row }
    for (const field of numericFields) {
      const currentValue = row[field]
      const previousValue = previous?.[field]
      output[field] = sameYear && previous?.reportType === expected && typeof currentValue === 'number' && typeof previousValue === 'number'
        ? currentValue - previousValue
        : null
    }
    const currentCashFlow = readObject(row.cashFlow)
    const previousCashFlow = readObject(previous?.cashFlow)
    if (currentCashFlow) {
      const cashFlow: Record<string, unknown> = { ...currentCashFlow }
      for (const field of cashFlowFields) {
        const currentValue = currentCashFlow[field]
        const previousValue = previousCashFlow?.[field]
        cashFlow[field] = row.reportType === 'Q1'
          ? currentValue
          : sameYear && previous?.reportType === expected && typeof currentValue === 'number' && typeof previousValue === 'number'
            ? currentValue - previousValue
            : null
      }
      output.cashFlow = cashFlow
    } else output.cashFlow = null
    refreshCashRatios(output)
    return output as T
  })
  if (basis === 'quarterly') return quarterly
  return quarterly.map((row, index) => {
    const window = quarterly.slice(Math.max(0, index - 3), index + 1)
    const output: Record<string, unknown> = { ...row }
    for (const field of numericFields) {
      const values = window.map((item) => item[field])
      output[field] = window.length === 4 && values.every((value) => typeof value === 'number')
        ? (values as number[]).reduce((sum, value) => sum + value, 0)
        : null
    }
    const latestCashFlow = readObject(row.cashFlow)
    if (latestCashFlow) {
      const cashFlow: Record<string, unknown> = { ...latestCashFlow }
      for (const field of cashFlowFields) {
        const values = window.map((item) => readObject(item.cashFlow)?.[field])
        cashFlow[field] = window.length === 4 && values.every((value) => typeof value === 'number')
          ? (values as number[]).reduce((sum, value) => sum + value, 0)
          : null
      }
      output.cashFlow = cashFlow
    } else output.cashFlow = null
    refreshCashRatios(output)
    return output as T
  })
}

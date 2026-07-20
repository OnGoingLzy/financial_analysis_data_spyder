export type Basis = 'cumulative' | 'quarterly' | 'ttm' | 'annual'
type RecordValue = { reportPeriod: string; reportType: string; [key: string]: unknown }
const numericFields = ['revenue', 'netProfit', 'netProfitToParent', 'grossProfit', 'operatingProfit', 'financialExpenses', 'salesExpenses', 'managementExpenses', 'researchExpenses']

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
    return output as T
  })
}

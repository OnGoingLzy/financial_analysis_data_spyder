const quarterOrder = { Q1: 0, H1: 1, Q3: 2, FY: 3 }

function safeDivide(numerator, denominator) {
  if (numerator == null || denominator == null || denominator === 0) return null
  return (numerator / denominator) * 100
}

export function deriveSingleQuarters(records, field) {
  const byYear = new Map()
  return [...records]
    .sort((a, b) => a.reportPeriod.localeCompare(b.reportPeriod))
    .map((record) => {
      const year = record.reportPeriod.slice(0, 4)
      const order = quarterOrder[record.reportType]
      const cumulative = record[field]
      let value = null
      if (cumulative != null && order === 0) value = cumulative
      else if (cumulative != null) {
        const previous = byYear.get(`${year}-${order - 1}`)
        if (previous != null) value = cumulative - previous
      }
      byYear.set(`${year}-${order}`, cumulative)
      return { ...record, value }
    })
}

export function calculateTtm(records, field) {
  const quarters = deriveSingleQuarters(records, field)
  if (quarters.length < 4) return null
  const recent = quarters.slice(-4)
  if (recent.some((item) => item.value == null)) return null
  return recent.reduce((sum, item) => sum + item.value, 0)
}

export function findLatestCommonPeriod(companyPeriods) {
  if (!companyPeriods.length) return null
  const common = new Set(companyPeriods[0])
  for (const periods of companyPeriods.slice(1)) {
    for (const period of [...common]) if (!periods.includes(period)) common.delete(period)
  }
  return [...common].sort().at(-1) ?? null
}

export function openingBalancePeriod(reportPeriod) {
  const year = Number(reportPeriod?.slice(0, 4))
  return Number.isFinite(year) ? `${year - 1}-12-31` : null
}

export function calculateRatios(income, balance, previousBalance) {
  const grossMargin = income.grossMargin ?? safeDivide(income.grossProfit, income.revenue)
  const netProfit = income.netProfitToParent ?? income.netProfit ?? null
  const netMargin = safeDivide(netProfit, income.revenue)
  const debtRatio = safeDivide(balance.totalLiabilities, balance.totalAssets)
  const receivablesToAssets = safeDivide(balance.accountsReceivable, balance.totalAssets)
  let roe = null
  let annualizedRoe = null
  if (previousBalance?.equityToParent != null && balance.equityToParent != null) {
    const averageEquity = (previousBalance.equityToParent + balance.equityToParent) / 2
    roe = safeDivide(netProfit, averageEquity)
    const factor = { Q1: 4, H1: 2, Q3: 4 / 3, FY: 1 }[income.reportType]
    annualizedRoe = roe == null || factor == null ? null : roe * factor
  }
  return { grossMargin, netMargin, debtRatio, receivablesToAssets, roe, annualizedRoe }
}

export function median(values) {
  const valid = values.filter((value) => value != null).sort((a, b) => a - b)
  if (!valid.length) return null
  const middle = Math.floor(valid.length / 2)
  return valid.length % 2 ? valid[middle] : (valid[middle - 1] + valid[middle]) / 2
}

export function percentileRank(value, values) {
  const valid = values.filter((item) => item != null).sort((a, b) => a - b)
  if (value == null || !valid.length) return null
  return valid.filter((item) => item <= value).length / valid.length * 100
}

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

export function findCommonPeriods(companyPeriods) {
  if (!companyPeriods.length) return []
  const common = new Set(companyPeriods[0])
  for (const periods of companyPeriods.slice(1)) {
    for (const period of [...common]) if (!periods.includes(period)) common.delete(period)
  }
  return [...common].sort((a, b) => b.localeCompare(a))
}

export function findLatestCommonPeriod(companyPeriods) {
  return findCommonPeriods(companyPeriods)[0] ?? null
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

function plainDivide(numerator, denominator) {
  if (numerator == null || denominator == null || denominator === 0) return null
  return numerator / denominator
}

function average(current, previous) {
  return current == null || previous == null ? null : (current + previous) / 2
}

function turnoverDays(averageBalance, flow, days) {
  const turnover = plainDivide(averageBalance, flow)
  return turnover == null || days == null ? null : turnover * days
}

export function calculatePeerMetrics(income = {}, balance = {}, previousBalance = null, cashFlow = null) {
  const netProfit = income.netProfitToParent ?? income.netProfit ?? null
  const days = { Q1: 90, H1: 181, Q3: 273, FY: 365 }[income.reportType] ?? null
  const averageAssets = previousBalance ? average(balance.totalAssets, previousBalance.totalAssets) : null
  const averageEquity = previousBalance ? average(balance.equityToParent, previousBalance.equityToParent) : null
  const averageReceivables = previousBalance ? average(balance.accountsReceivable, previousBalance.accountsReceivable) : null
  const averageInventory = previousBalance ? average(balance.inventory, previousBalance.inventory) : null
  const averagePayables = previousBalance ? average(balance.accountsPayable, previousBalance.accountsPayable) : null
  const receivableDays = turnoverDays(averageReceivables, income.revenue, days)
  const inventoryDays = turnoverDays(averageInventory, income.operatingCost, days)
  const payableDays = turnoverDays(averagePayables, income.operatingCost, days)
  const assetTurnover = plainDivide(income.revenue, averageAssets)
  const equityMultiplier = plainDivide(averageAssets, averageEquity)
  const roe = safeDivide(netProfit, averageEquity)
  const cashProfitRatio = plainDivide(cashFlow?.netOperatingCashFlow, netProfit)
  return {
    grossMargin: income.grossMargin ?? safeDivide(income.grossProfit, income.revenue),
    netMargin: safeDivide(netProfit, income.revenue),
    operatingMargin: safeDivide(income.operatingProfit, income.revenue),
    deductedNetMargin: safeDivide(income.netProfitAfterNonRecurring, income.revenue),
    salesExpenseRatio: safeDivide(income.salesExpenses, income.revenue),
    managementExpenseRatio: safeDivide(income.managementExpenses, income.revenue),
    researchExpenseRatio: safeDivide(income.researchExpenses, income.revenue),
    financialExpenseRatio: safeDivide(income.financialExpenses, income.revenue),
    debtRatio: safeDivide(balance.totalLiabilities, balance.totalAssets),
    currentRatio: plainDivide(balance.currentAssets, balance.currentLiabilities),
    quickRatio: plainDivide(balance.currentAssets == null || balance.inventory == null ? null : balance.currentAssets - balance.inventory, balance.currentLiabilities),
    cashShortDebtRatio: plainDivide(balance.monetaryFunds, balance.shortTermBorrowings),
    interestCoverage: plainDivide(income.totalProfit == null || income.interestExpenses == null ? null : income.totalProfit + income.interestExpenses, income.interestExpenses),
    cashProfitRatio,
    cashRevenueRatio: safeDivide(cashFlow?.cashReceivedFromSales, income.revenue),
    freeCashFlow: cashFlow?.netOperatingCashFlow == null || cashFlow?.capitalExpenditure == null ? null : cashFlow.netOperatingCashFlow - cashFlow.capitalExpenditure,
    receivableDays,
    inventoryDays,
    payableDays,
    cashConversionCycle: receivableDays == null || inventoryDays == null || payableDays == null ? null : receivableDays + inventoryDays - payableDays,
    roe,
    assetTurnover,
    equityMultiplier,
  }
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

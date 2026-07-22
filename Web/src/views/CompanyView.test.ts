import { flushPromises, shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { apiGet } from '@/api/client'
import CompanyView from './CompanyView.vue'

const routeState = vi.hoisted(() => ({ params: { code: 'SH600998' }, query: {} as Record<string, string> }))

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({ replace: vi.fn() }),
}))

vi.mock('@/api/client', () => ({
  apiGet: vi.fn(),
  ApiClientError: class ApiClientError extends Error {},
}))

function response(cashFlowAvailable: boolean) {
  return {
    company: { code: 'SH600998', name: '九州通', market: 'SH', industryName: '医药流通', cashFlowAvailable },
    cashFlowNotice: cashFlowAvailable ? null : '当前公司尚未补采现金流量表。',
    records: [{
      reportPeriod: '2025-12-31', reportType: 'FY', revenue: 1000, grossProfit: 200, grossMargin: 20,
      netProfit: 100, netProfitToParent: 95, revenueYoyGrowth: 8, financialExpenses: 5,
      salesExpenses: 40, managementExpenses: 30, researchExpenses: 20, operatingProfit: 120,
      balance: { totalAssets: 2000, totalLiabilities: 1200 },
      cashFlow: cashFlowAvailable ? { reportPeriod: '2025-12-31', reportType: 'FY', netOperatingCashFlow: 100, netInvestingCashFlow: -30, netFinancingCashFlow: 10, cashReceivedFromSales: 900, capitalExpenditure: 30, endingCashAndEquivalents: 200 } : null,
      ratios: { grossMargin: 20, netMargin: 9.5, debtRatio: 60, cashProfitRatio: 100 / 95, cashRevenueRatio: 90, freeCashFlow: 70 },
    }],
  }
}

describe('公司现金流分析', () => {
  beforeEach(() => vi.mocked(apiGet).mockReset())

  it('存在标准现金流数据时展示现金流质量与报告期明细', async () => {
    vi.mocked(apiGet).mockResolvedValue(response(true) as never)
    const wrapper = shallowMount(CompanyView)
    await flushPromises()

    expect(wrapper.text()).toContain('现金流质量')
    expect(wrapper.text()).toContain('经营活动现金流净额')
    expect(wrapper.text()).toContain('销售收现')
    expect(wrapper.text()).not.toContain('现金流量分析暂不可用')
  })

  it('当前公司没有现金流数据时保留明确空状态', async () => {
    vi.mocked(apiGet).mockResolvedValue(response(false) as never)
    const wrapper = shallowMount(CompanyView)
    await flushPromises()

    expect(wrapper.text()).toContain('现金流量分析暂不可用')
    expect(wrapper.text()).toContain('当前公司尚未补采现金流量表')
  })
})

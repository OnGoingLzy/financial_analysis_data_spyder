import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'

import { useAnalysisStore } from '@/stores/analysis'
import CompanyDirectoryView from './CompanyDirectoryView.vue'

describe('公司查询主页', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    useAnalysisStore().companies = [
      { code: 'SH600056', name: '中国医药', market: '上海', industryName: '医药流通', latestPeriod: '2025-12-31' },
      { code: 'SZ000001', name: '平安银行', market: '深圳', industryName: '银行', latestPeriod: '2025-09-30' },
    ]
  })

  function mountView() {
    return mount(CompanyDirectoryView, {
      global: {
        stubs: {
          RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' },
        },
      },
    })
  }

  it('按名称或代码搜索，并提供明确的详情入口', async () => {
    const wrapper = mountView()
    expect(wrapper.text()).toContain('中国医药')
    expect(wrapper.text()).toContain('平安银行')

    await wrapper.get('[data-testid="company-search"]').setValue('600056')

    expect(wrapper.text()).toContain('中国医药')
    expect(wrapper.text()).not.toContain('平安银行')
    expect(wrapper.findAll('a[href="/company/SH600056"]').some((link) => link.text().includes('进入分析'))).toBe(true)
  })

  it('支持市场和行业筛选', async () => {
    const wrapper = mountView()
    await wrapper.get('[data-testid="market-filter"]').setValue('深圳')
    expect(wrapper.text()).toContain('平安银行')
    expect(wrapper.text()).not.toContain('中国医药')

    await wrapper.get('[data-testid="market-filter"]').setValue('')
    await wrapper.get('[data-testid="industry-filter"]').setValue('医药流通')
    expect(wrapper.text()).toContain('中国医药')
    expect(wrapper.text()).not.toContain('平安银行')
  })
})

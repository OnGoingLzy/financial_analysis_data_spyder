import { createPinia, setActivePinia } from 'pinia'
import { flushPromises, shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { apiGet } from '@/api/client'
import { useAnalysisStore } from '@/stores/analysis'
import CompareView from './CompareView.vue'

const routeState = vi.hoisted(() => ({ query: { codes: 'SH600998,SH600056', mode: 'absolute', period: '' } as Record<string, string> }))
const replaceRoute = vi.hoisted(() => vi.fn())

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({ replace: replaceRoute }),
}))

vi.mock('@/api/client', () => ({
  apiGet: vi.fn(),
  ApiClientError: class ApiClientError extends Error {},
}))

function response(period = '2025-12-31', availablePeriods = ['2025-12-31', '2025-09-30']) {
  return {
    availablePeriods,
    commonPeriod: period,
    mode: 'absolute',
    sampleSize: 2,
    medians: {},
    rows: [
      { code: 'SH600998', name: '九州通', market: 'SH', industryName: null, metrics: { revenue: { value: 100, rawValue: 100 } }, profile: {} },
      { code: 'SH600056', name: '中国医药', market: 'SH', industryName: null, metrics: { revenue: { value: 80, rawValue: 80 } }, profile: {} },
    ],
  }
}

describe('同行对比报告期选择', () => {
  beforeEach(() => {
    vi.stubGlobal('localStorage', { getItem: vi.fn(() => null), setItem: vi.fn() })
    setActivePinia(createPinia())
    useAnalysisStore().companies = [
      { code: 'SH600998', name: '九州通', market: 'SH', industryName: null },
      { code: 'SH600056', name: '中国医药', market: 'SH', industryName: null },
    ]
    routeState.query = { codes: 'SH600998,SH600056', mode: 'absolute', period: '' }
    replaceRoute.mockReset()
    vi.mocked(apiGet).mockImplementation(async (path) => {
      const period = new URLSearchParams(path.split('?')[1]).get('period') ?? '2025-12-31'
      return response(period) as never
    })
  })

  it('展示共同报告期并在切换后携带 period 重新加载', async () => {
    const wrapper = shallowMount(CompareView, { global: { stubs: { RouterLink: true } } })
    await flushPromises()

    const selector = wrapper.get('[data-testid="compare-period"]')
    expect((selector.element as HTMLSelectElement).value).toBe('2025-12-31')
    expect(selector.findAll('option').map((option) => option.text())).toEqual([
      '2025 年报 · 2025-12-31',
      '2025 三季报 · 2025-09-30',
    ])

    await selector.setValue('2025-09-30')
    await flushPromises()

    expect(vi.mocked(apiGet).mock.calls.at(-1)?.[0]).toContain('period=2025-09-30')
    expect(replaceRoute).toHaveBeenLastCalledWith(expect.stringContaining('period=2025-09-30'))
  })

  it('加载中或只有一个共同报告期时禁用选择器', async () => {
    vi.mocked(apiGet).mockResolvedValueOnce(response('2025-12-31', ['2025-12-31']) as never)
    const wrapper = shallowMount(CompareView, { global: { stubs: { RouterLink: true } } })
    await flushPromises()
    expect(wrapper.get('[data-testid="compare-period"]').attributes('disabled')).toBeDefined()
  })
})

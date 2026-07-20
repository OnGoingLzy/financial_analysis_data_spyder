import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ErrorState from './ErrorState.vue'

describe('错误状态', () => {
  it('展示中文说明、错误码并允许重试', async () => {
    const wrapper = mount(ErrorState, { props: { code: 'DATABASE_NOT_FOUND', message: '未找到财务数据库' } })
    expect(wrapper.text()).toContain('未找到财务数据库')
    expect(wrapper.text()).toContain('DATABASE_NOT_FOUND')
    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('retry')).toHaveLength(1)
  })
})

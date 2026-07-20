import { defineStore } from 'pinia'
import { ref } from 'vue'

import { apiGet, ApiClientError } from '@/api/client'
import type { Company, Meta } from '@/types/financial'

export const useAnalysisStore = defineStore('analysis', () => {
  const meta = ref<Meta | null>(null)
  const companies = ref<Company[]>([])
  const loading = ref(false)
  const error = ref<ApiClientError | null>(null)

  async function initialize() {
    loading.value = true
    error.value = null
    try {
      const [metaResult, companyResult] = await Promise.all([
        apiGet<Meta>('/api/meta'),
        apiGet<Company[]>('/api/companies'),
      ])
      meta.value = metaResult
      companies.value = companyResult
    } catch (cause) {
      error.value = cause instanceof ApiClientError ? cause : new ApiClientError({ code: 'NETWORK_ERROR', message: '无法连接本地分析服务', retryable: true, scope: 'application' })
    } finally {
      loading.value = false
    }
  }

  return { meta, companies, loading, error, initialize }
})

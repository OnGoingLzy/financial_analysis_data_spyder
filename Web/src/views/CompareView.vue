<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { apiGet, ApiClientError } from '@/api/client'
import ErrorState from '@/components/ErrorState.vue'
import LoadingState from '@/components/LoadingState.vue'
import MetricValue from '@/components/MetricValue.vue'
import ScaleGrowthChart from '@/components/charts/ScaleGrowthChart.vue'
import ProfitabilityChart from '@/components/charts/ProfitabilityChart.vue'
import PeerHeatmapChart from '@/components/charts/PeerHeatmapChart.vue'
import GrowthProfitChart from '@/components/charts/GrowthProfitChart.vue'
import IncomeStructureChart from '@/components/charts/IncomeStructureChart.vue'
import WorkingCapitalChart from '@/components/charts/WorkingCapitalChart.vue'
import CashRiskChart from '@/components/charts/CashRiskChart.vue'
import { useAnalysisStore } from '@/stores/analysis'
import type { CompareResponse } from '@/types/financial'
import { buildCompareQuery } from './viewModel'

const store = useAnalysisStore()
const route = useRoute()
const router = useRouter()
const result = ref<CompareResponse | null>(null)
const loading = ref(false)
const error = ref<ApiClientError | null>(null)
const mode = ref(String(route.query.mode ?? 'absolute'))
const selectedPeriod = ref(String(route.query.period ?? ''))
const selectedCodes = ref<string[]>(String(route.query.codes ?? '').split(',').filter(Boolean))
let controller: AbortController | null = null

const metricDefinitions = [
  { key: 'revenue', label: '营业收入', format: 'amount' as const },
  { key: 'netProfitToParent', label: '归母净利润', format: 'amount' as const },
  { key: 'grossMargin', label: '毛利率', format: 'percent' as const },
  { key: 'netMargin', label: '净利率', format: 'percent' as const },
  { key: 'debtRatio', label: '资产负债率', format: 'percent' as const },
  { key: 'revenueYoyGrowth', label: '营收同比', format: 'percent' as const },
]
const comparisonRows = computed(() => result.value?.rows ?? [])
const chartRows = computed(() => comparisonRows.value.map((row) => ({ name: row.name, value: row.metrics.revenue?.value ?? null })))
const marginRows = computed(() => comparisonRows.value.map((row) => ({ name: row.name, value: row.metrics.netMargin?.value ?? null })))
const leadingCompany = computed(() => [...comparisonRows.value].filter((row) => row.metrics.revenue?.rawValue != null).sort((a, b) => (b.metrics.revenue.rawValue ?? 0) - (a.metrics.revenue.rawValue ?? 0))[0])

function formatPeriod(period: string) {
  const reportName = ({ '03-31': '一季报', '06-30': '中报', '09-30': '三季报', '12-31': '年报' } as Record<string, string>)[period.slice(5)] ?? '报告期'
  return `${period.slice(0, 4)} ${reportName} · ${period}`
}

function toggleCompany(code: string) {
  if (selectedCodes.value.includes(code)) selectedCodes.value = selectedCodes.value.filter((item) => item !== code)
  else if (selectedCodes.value.length < 12) selectedCodes.value = [...selectedCodes.value, code]
}

async function loadComparison() {
  if (selectedCodes.value.length < 2) return
  controller?.abort()
  controller = new AbortController()
  loading.value = true
  error.value = null
  try {
    const query = buildCompareQuery(selectedCodes.value, mode.value, selectedPeriod.value || null)
    result.value = await apiGet<CompareResponse>(`/api/compare?${query}`, controller.signal)
    selectedPeriod.value = result.value.commonPeriod
    const normalizedQuery = buildCompareQuery(selectedCodes.value, mode.value, result.value.commonPeriod)
    await router.replace(`/compare?${normalizedQuery}`)
    localStorage.setItem('financial-selected-companies', selectedCodes.value.join(','))
  } catch (cause) {
    if ((cause as Error).name !== 'AbortError') error.value = cause as ApiClientError
  } finally {
    loading.value = false
  }
}

function setMode(nextMode: string) { mode.value = nextMode; void loadComparison() }

watch(() => route.query.period, (period) => {
  const nextPeriod = String(period ?? '')
  if (nextPeriod && nextPeriod !== selectedPeriod.value) {
    selectedPeriod.value = nextPeriod
    void loadComparison()
  }
})

onMounted(() => {
  if (selectedCodes.value.length < 2) {
    const saved = localStorage.getItem('financial-selected-companies')?.split(',').filter(Boolean) ?? []
    selectedCodes.value = saved.length >= 2 ? saved : store.companies.slice(0, 6).map((company) => company.code)
  }
  void loadComparison()
})
onBeforeUnmount(() => controller?.abort())
</script>

<template>
  <section>
    <header class="page-head">
      <div><h1 class="page-title">同行横向对比</h1><p class="page-intro">统一报告期比较规模、盈利质量与财务结构。缺失值不参与中位数和分位计算。</p></div>
      <div class="status-line"><span class="status-dot"></span><span>{{ result?.commonPeriod ?? '共同报告期计算中' }} / {{ result?.sampleSize ?? selectedCodes.length }} 家样本</span></div>
    </header>

    <section class="panel filter-panel" aria-label="对比筛选">
      <div class="toolbar">
        <div class="mode-group" role="group" aria-label="比较模式">
          <button v-for="item in [{k:'absolute',l:'绝对值'}, {k:'index',l:'中位数指数'}, {k:'percentile',l:'分位排名'}]" :key="item.k" class="button" type="button" :aria-pressed="mode === item.k" @click="setMode(item.k)">{{ item.l }}</button>
        </div>
        <div class="field period-field">
          <!-- <label for="compare-period">报告期</label> -->
          <select id="compare-period" v-model="selectedPeriod" data-testid="compare-period" :disabled="loading || (result?.availablePeriods.length ?? 0) <= 1" @change="loadComparison">
            <option v-for="period in result?.availablePeriods ?? []" :key="period" :value="period">{{ formatPeriod(period) }}</option>
          </select>
        </div>
        <button class="button primary" type="button" :disabled="loading || selectedCodes.length < 2" @click="loadComparison">更新分析</button>
        <span class="terminal-meta">最多 12 家 · 当前 {{ selectedCodes.length }} 家</span>
      </div>
      <details class="company-selector">
        <summary>选择对比公司</summary>
        <div class="company-options">
          <label v-for="company in store.companies" :key="company.code" :class="{ selected: selectedCodes.includes(company.code) }">
            <input type="checkbox" :checked="selectedCodes.includes(company.code)" :disabled="!selectedCodes.includes(company.code) && selectedCodes.length >= 12" @change="toggleCompany(company.code)">
            <span>{{ company.name }}</span><small>{{ company.code }}</small>
          </label>
        </div>
      </details>
    </section>

    <LoadingState v-if="loading && !result" />
    <ErrorState v-else-if="error" :code="error.code" :message="error.message" @retry="loadComparison" />
    <template v-else-if="result">
      <section class="insight-strip">
        <div><span>样本结论</span><strong>{{ leadingCompany?.name ?? '暂无' }} 的营收规模居首</strong></div>
        <p>指数模式以所选样本中位数为 100；分位排名同时展示样本量，不混用不同报告期。</p>
      </section>
      <div class="content-grid">
        <ScaleGrowthChart :rows="chartRows" title="营收规模对比" :description="mode === 'absolute' ? '统一报告期累计营业收入' : mode === 'index' ? '样本中位数 = 100' : '样本内分位排名'" />
        <ProfitabilityChart :rows="marginRows" title="净利率横截面" description="归母净利润 / 营业收入；负值使用绿色" />
      </div>
      <section class="analysis-section"><header><h2>综合判断</h2><p>统一报告期下比较质量分位与增长盈利位置。</p></header><div class="diagnostic-grid"><PeerHeatmapChart :rows="comparisonRows" /><GrowthProfitChart :rows="comparisonRows" /></div></section>
      <section class="analysis-section"><header><h2>利润形成</h2><p>将每百元收入拆分到成本、费用和最终利润。</p></header><IncomeStructureChart :rows="comparisonRows" /></section>
      <section class="analysis-section"><header><h2>资金效率与风险</h2><p>新字段缺失时保持空状态，重新采集后自动解锁。</p></header><div class="diagnostic-grid"><WorkingCapitalChart :rows="comparisonRows" /><CashRiskChart :rows="comparisonRows" /></div></section>
      <section class="panel comparison-table">
        <header class="panel-header"><div><h2>指标矩阵 · {{ result.commonPeriod }}</h2><p>所有数值均来自标准化正式表</p></div></header>
        <div class="table-scroll"><table><caption class="sr-only">同行财务指标矩阵</caption><thead><tr><th>公司</th><th v-for="metric in metricDefinitions" :key="metric.key">{{ metric.label }}</th></tr></thead><tbody><tr v-for="row in comparisonRows" :key="row.code"><td><RouterLink class="company-link" :to="`/company/${row.code}`"><strong>{{ row.name }}</strong><small>{{ row.code }}</small></RouterLink></td><td v-for="metric in metricDefinitions" :key="metric.key"><MetricValue :value="row.metrics[metric.key]?.value ?? null" :format="mode === 'absolute' ? metric.format : 'number'" :kind="metric.key === 'debtRatio' ? 'neutral' : 'profit'" /><small v-if="mode === 'percentile' && row.metrics[metric.key]?.percentile != null">P{{ Math.round(row.metrics[metric.key].percentile ?? 0) }} / n={{ result.sampleSize }}</small></td></tr></tbody></table></div>
      </section>
    </template>
  </section>
</template>

<style scoped>
.filter-panel { margin-bottom: var(--space-md); }.mode-group { display: flex; gap: var(--space-2xs); }.period-field { min-width: 14rem; }.period-field select { font-family: var(--font-data); }.company-selector { border-top: var(--rule-thin) solid var(--color-rule); }.company-selector summary { padding: var(--space-sm) var(--space-md); color: var(--color-accent); cursor: pointer; font-size: var(--text-sm); }.company-options { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--space-2xs); padding: 0 var(--space-md) var(--space-md); }.company-options label { display: grid; grid-template-columns: auto 1fr; gap: 0 var(--space-xs); padding: var(--space-xs); border: var(--rule-thin) solid var(--color-rule); color: var(--color-ink-muted); cursor: pointer; }.company-options label.selected { border-color: var(--color-accent); background: var(--color-accent-wash); color: var(--color-ink); }.company-options small { grid-column: 2; color: var(--color-ink-faint); font: var(--text-xs) var(--font-data); }.insight-strip { display: grid; grid-template-columns: minmax(15rem, .7fr) 1.3fr; gap: var(--space-xl); margin: var(--space-md) 0; padding: var(--space-lg) 0; border-top: var(--rule-strong) solid var(--color-accent); border-bottom: var(--rule-thin) solid var(--color-rule); }.insight-strip span { display: block; color: var(--color-accent); font: var(--text-xs) var(--font-data); }.insight-strip strong { display: block; margin-top: var(--space-xs); font-size: var(--text-lg); }.insight-strip p { margin: 0; color: var(--color-ink-muted); }.comparison-table { margin-top: var(--space-md); }.panel-header p { margin: var(--space-2xs) 0 0; color: var(--color-ink-muted); font-size: var(--text-xs); }.company-link { display: grid; }.company-link:hover strong { color: var(--color-accent); }.company-link small, td > small { display: block; color: var(--color-ink-faint); font: var(--text-xs) var(--font-data); }td > small { margin-top: var(--space-2xs); }@media (max-width: 900px) { .company-options { grid-template-columns: repeat(2, minmax(0, 1fr)); } }@media (max-width: 560px) { .company-options, .insight-strip { grid-template-columns: 1fr; } .mode-group, .period-field { width: 100%; overflow-x: auto; } }
.analysis-section { margin-top: var(--space-xl); }
.analysis-section > header { display: flex; align-items: baseline; justify-content: space-between; gap: var(--space-lg); margin-bottom: var(--space-sm); padding-bottom: var(--space-sm); border-bottom: var(--rule-thin) solid var(--color-rule); }
.analysis-section > header h2 { margin: 0; font-size: var(--text-lg); }
.analysis-section > header p { margin: 0; color: var(--color-ink-muted); font-size: var(--text-xs); }
.diagnostic-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-md); }
@media (max-width: 900px) { .diagnostic-grid { grid-template-columns: 1fr; } }
</style>

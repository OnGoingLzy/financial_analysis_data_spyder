<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiGet, ApiClientError } from '@/api/client'
import ErrorState from '@/components/ErrorState.vue'
import FormulaNote from '@/components/FormulaNote.vue'
import LoadingState from '@/components/LoadingState.vue'
import MetricValue from '@/components/MetricValue.vue'
import CompanyCashFlowChart from '@/components/charts/CompanyCashFlowChart.vue'
import CompanyTrendChart from '@/components/charts/CompanyTrendChart.vue'
import type { AnalysisRecord, Company } from '@/types/financial'
import { financialExpenseLabel, reportTypeLabel } from '@/utils/format'
import { deriveBasisRecords, type Basis } from './viewModel'

interface AnalysisResponse { company: Company & { cashFlowAvailable: boolean }; records: AnalysisRecord[]; cashFlowNotice: string | null }
const route = useRoute(); const router = useRouter()
const data = ref<AnalysisResponse | null>(null); const loading = ref(false); const error = ref<ApiClientError | null>(null)
const basis = ref<Basis>((route.query.basis as Basis) ?? 'cumulative')
const basisOptions: Array<{ key: Basis; label: string }> = [{ key: 'cumulative', label: '累计' }, { key: 'quarterly', label: '单季度' }, { key: 'ttm', label: 'TTM' }, { key: 'annual', label: '年度' }]
const records = computed(() => deriveBasisRecords(data.value?.records ?? [], basis.value))
const latest = computed(() => records.value.at(-1) ?? null)
const cashFlowRecords = computed(() => records.value.filter((row) => {
  const cashFlow = row.cashFlow
  return cashFlow && [cashFlow.netOperatingCashFlow, cashFlow.netInvestingCashFlow, cashFlow.netFinancingCashFlow, cashFlow.cashReceivedFromSales, cashFlow.capitalExpenditure, cashFlow.endingCashAndEquivalents].some((value) => value != null)
}))
const latestCashFlowRecord = computed(() => cashFlowRecords.value.at(-1) ?? null)

async function load() { loading.value = true; error.value = null; try { data.value = await apiGet<AnalysisResponse>(`/api/companies/${route.params.code}/analysis`) } catch (cause) { error.value = cause as ApiClientError } finally { loading.value = false } }
function setBasis(next: Basis) { basis.value = next; void router.replace({ query: { ...route.query, basis: next } }) }
onMounted(load); watch(() => route.params.code, load)
</script>
<template>
  <section>
    <header class="page-head"><div><p class="terminal-meta">{{ data?.company.code ?? route.params.code }} / COMPANY RESEARCH</p><h1 class="page-title">{{ data?.company.name ?? '公司财务分析' }}</h1><p class="page-intro">从盈利、成长、费用和资产负债四个方向追踪经营质量，所有口径共用同一标准化数据源。</p></div><div class="status-line"><span class="status-dot"></span><span>{{ latest?.reportPeriod ?? '读取中' }} · {{ latest ? reportTypeLabel(latest.reportType) : '—' }}</span></div></header>
    <div class="basis-bar panel" role="group" aria-label="报表口径"><span>分析口径</span><button v-for="item in basisOptions" :key="item.key" class="button" :aria-pressed="basis === item.key" @click="setBasis(item.key)">{{ item.label }}</button><small>单季度由累计值差分；TTM 需连续四季</small></div>
    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :code="error.code" :message="error.message" @retry="load" />
    <template v-else-if="data && latest">
      <section class="metric-grid panel summary-grid">
        <div class="metric-cell"><div class="metric-label">营业收入</div><div class="metric-value"><MetricValue :value="latest.revenue" /></div><div class="metric-note">{{ basisOptions.find((item) => item.key === basis)?.label }}口径</div></div>
        <div class="metric-cell"><div class="metric-label">归母净利润</div><div class="metric-value"><MetricValue :value="latest.netProfitToParent ?? latest.netProfit" /></div><div class="metric-note">亏损以绿色标记</div></div>
        <div class="metric-cell"><div class="metric-label">营收同比</div><div class="metric-value"><MetricValue :value="latest.revenueYoyGrowth" format="percent" /></div><div class="metric-note">正增长红 / 负增长绿</div></div>
        <div class="metric-cell"><div class="metric-label">资产负债率</div><div class="metric-value"><MetricValue :value="latest.ratios?.debtRatio" format="percent" kind="neutral" /></div><div class="metric-note">总负债 / 总资产</div></div>
      </section>
      <div class="content-grid"><CompanyTrendChart :records="records" :title="`${basisOptions.find((item) => item.key === basis)?.label}经营趋势`" /><section class="panel diagnostic"><header class="panel-header"><h2>盈利诊断</h2></header><dl><div><dt>毛利率</dt><dd><MetricValue :value="latest.ratios?.grossMargin ?? latest.grossMargin" format="percent" /></dd></div><div><dt>净利率</dt><dd><MetricValue :value="latest.ratios?.netMargin" format="percent" /></dd></div><div><dt>年化 ROE（估算）</dt><dd><MetricValue :value="latest.ratios?.annualizedRoe" format="percent" /></dd></div><div><dt>{{ financialExpenseLabel(latest.financialExpenses) }}</dt><dd><MetricValue :value="latest.financialExpenses" /></dd></div></dl><FormulaNote title="查看 ROE 估算公式" formula="累计归母净利润 ÷ 平均归母净资产 × 年化因子；缺少期初净资产时返回暂无数据。" /></section></div>
      <section class="panel detail-table"><header class="panel-header"><div><h2>报告期明细 · {{ records.length }} 期</h2><p>金额单位：人民币元；比率单位：百分点</p></div></header><div class="table-scroll"><table><caption class="sr-only">公司报告期明细</caption><thead><tr><th>报告期</th><th>营业收入</th><th>净利润</th><th>毛利率</th><th>营收同比</th><th>财务费用 / 收益</th><th>总资产</th><th>总负债</th></tr></thead><tbody><tr v-for="row in [...records].reverse()" :key="row.reportPeriod"><td>{{ row.reportPeriod }}<small>{{ reportTypeLabel(row.reportType) }}</small></td><td><MetricValue :value="row.revenue" /></td><td><MetricValue :value="row.netProfitToParent ?? row.netProfit" /></td><td><MetricValue :value="row.ratios?.grossMargin ?? row.grossMargin" format="percent" /></td><td><MetricValue :value="row.revenueYoyGrowth" format="percent" /></td><td><span class="expense-label">{{ financialExpenseLabel(row.financialExpenses) }}</span><MetricValue :value="row.financialExpenses" /></td><td><MetricValue :value="row.balance?.totalAssets" kind="neutral" /></td><td><MetricValue :value="row.balance?.totalLiabilities" kind="neutral" /></td></tr></tbody></table></div></section>
      <section v-if="latestCashFlowRecord" class="cash-flow-section">
        <header class="section-head"><div><p class="terminal-meta">CASH FLOW QUALITY</p><h2>现金流质量</h2><p>从现金创造、收入收现和资本开支三个角度检验利润含金量。</p></div><span>{{ cashFlowRecords.length }} 个有效报告期</span></header>
        <section class="metric-grid panel cash-flow-metrics">
          <div class="metric-cell"><div class="metric-label">经营活动现金流净额</div><div class="metric-value"><MetricValue :value="latestCashFlowRecord.cashFlow?.netOperatingCashFlow" /></div><div class="metric-note">净流入红 / 净流出绿</div></div>
          <div class="metric-cell"><div class="metric-label">现金含量</div><div class="metric-value"><MetricValue :value="latestCashFlowRecord.ratios?.cashProfitRatio" format="number" kind="neutral" /></div><div class="metric-note">经营现金流 ÷ 归母净利润</div></div>
          <div class="metric-cell"><div class="metric-label">现金收入比</div><div class="metric-value"><MetricValue :value="latestCashFlowRecord.ratios?.cashRevenueRatio" format="percent" kind="neutral" /></div><div class="metric-note">销售收现 ÷ 营业收入</div></div>
          <div class="metric-cell"><div class="metric-label">自由现金流</div><div class="metric-value"><MetricValue :value="latestCashFlowRecord.ratios?.freeCashFlow" /></div><div class="metric-note">经营现金流 − 资本开支</div></div>
        </section>
        <CompanyCashFlowChart :records="cashFlowRecords" />
        <section class="panel detail-table cash-flow-table"><header class="panel-header"><div><h2>现金流报告期明细</h2><p>金额单位：人民币元；缺失字段保持暂无数据</p></div></header><div class="table-scroll"><table><caption class="sr-only">现金流报告期明细</caption><thead><tr><th>报告期</th><th>经营现金流</th><th>投资现金流</th><th>筹资现金流</th><th>销售收现</th><th>资本开支</th><th>期末现金及等价物</th></tr></thead><tbody><tr v-for="row in [...cashFlowRecords].reverse()" :key="row.reportPeriod"><td>{{ row.reportPeriod }}<small>{{ reportTypeLabel(row.reportType) }}</small></td><td><MetricValue :value="row.cashFlow?.netOperatingCashFlow" /></td><td><MetricValue :value="row.cashFlow?.netInvestingCashFlow" /></td><td><MetricValue :value="row.cashFlow?.netFinancingCashFlow" /></td><td><MetricValue :value="row.cashFlow?.cashReceivedFromSales" /></td><td><MetricValue :value="row.cashFlow?.capitalExpenditure" kind="neutral" /></td><td><MetricValue :value="row.cashFlow?.endingCashAndEquivalents" kind="neutral" /></td></tr></tbody></table></div></section>
      </section>
      <section v-else class="cash-flow-note panel"><div><h2>现金流量分析暂不可用</h2><p>{{ data.cashFlowNotice ?? `当前${basisOptions.find((item) => item.key === basis)?.label}口径没有可用现金流数据。` }}</p></div></section>
    </template>
  </section>
</template>
<style scoped>
.basis-bar { display: flex; align-items: center; gap: var(--space-xs); margin-bottom: var(--space-md); padding: var(--space-sm) var(--space-md); }.basis-bar > span { margin-right: var(--space-sm); color: var(--color-ink-muted); font-size: var(--text-xs); }.basis-bar small { margin-left: auto; color: var(--color-ink-faint); }.summary-grid { margin-bottom: var(--space-md); }.diagnostic dl { margin: 0; }.diagnostic dl div { display: flex; justify-content: space-between; gap: var(--space-md); padding: var(--space-sm) var(--space-lg); border-bottom: var(--rule-thin) solid var(--color-rule); }.diagnostic dt { color: var(--color-ink-muted); }.diagnostic dd { margin: 0; }.detail-table { margin-top: var(--space-md); }.panel-header p { margin: var(--space-2xs) 0 0; color: var(--color-ink-muted); font-size: var(--text-xs); }.detail-table td:first-child small { display: block; color: var(--color-ink-faint); }.expense-label { display: block; color: var(--color-ink-faint); font: var(--text-xs) var(--font-body); }.cash-flow-section { margin-top: var(--space-xl); }.section-head { display: flex; align-items: end; justify-content: space-between; gap: var(--space-lg); margin-bottom: var(--space-md); }.section-head h2 { margin: var(--space-2xs) 0; font-size: var(--text-xl); }.section-head p:not(.terminal-meta), .section-head > span { margin: 0; color: var(--color-ink-muted); font-size: var(--text-xs); }.cash-flow-metrics { margin-bottom: var(--space-md); }.cash-flow-table { margin-top: var(--space-md); }.cash-flow-note { margin-top: var(--space-md); padding: var(--space-lg); border-top: var(--rule-strong) solid var(--color-warning); }.cash-flow-note h2 { margin-bottom: var(--space-xs); font-size: var(--text-md); }.cash-flow-note p { margin: 0; color: var(--color-ink-muted); }@media (max-width: 720px) { .basis-bar { overflow-x: auto; }.basis-bar small { display: none; }.section-head { align-items: start; flex-direction: column; } }
</style>

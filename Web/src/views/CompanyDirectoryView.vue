<script setup lang="ts">
import { computed, ref } from 'vue'

import EmptyState from '@/components/EmptyState.vue'
import { useAnalysisStore } from '@/stores/analysis'

const store = useAnalysisStore()
const keyword = ref('')
const market = ref('')
const industry = ref('')

const markets = computed(() => [...new Set(store.companies.map((company) => company.market).filter(Boolean))].sort())
const industries = computed(() => [...new Set(store.companies.map((company) => company.industryName).filter((value): value is string => Boolean(value)))].sort())
const companies = computed(() => {
  const query = keyword.value.trim().toLocaleLowerCase('zh-CN')
  return store.companies.filter((company) => (
    (!query || company.name.toLocaleLowerCase('zh-CN').includes(query) || company.code.toLocaleLowerCase('zh-CN').includes(query))
    && (!market.value || company.market === market.value)
    && (!industry.value || company.industryName === industry.value)
  ))
})

function marketLabel(value: string) {
  return ({ SH: '上海证券交易所', SZ: '深圳证券交易所', BJ: '北京证券交易所' } as Record<string, string>)[value] ?? value
}

function resetFilters() {
  keyword.value = ''
  market.value = ''
  industry.value = ''
}
</script>

<template>
  <header class="page-head">
    <div>
      <p class="terminal-meta">COMPANY DIRECTORY / 研究对象目录</p>
      <h1 class="page-title">公司查询</h1>
      <p class="page-intro">从标准化财务数据库中选择研究对象，再进入单家公司深度分析。页面不会代替你预选任何公司。</p>
    </div>
    <div class="directory-count"><strong>{{ companies.length }}</strong><span>/ {{ store.companies.length }} 家公司</span></div>
  </header>

  <section class="panel filter-panel" aria-label="公司筛选">
    <div class="toolbar">
      <div class="field search-field">
        <label for="company-search">公司名称 / 证券代码</label>
        <input id="company-search" v-model="keyword" data-testid="company-search" type="search" placeholder="例如：中国医药、600056" autocomplete="off">
      </div>
      <div class="field">
        <label for="market-filter">上市市场</label>
        <select id="market-filter" v-model="market" data-testid="market-filter">
          <option value="">全部市场</option>
          <option v-for="item in markets" :key="item" :value="item">{{ marketLabel(item) }}</option>
        </select>
      </div>
      <div class="field">
        <label for="industry-filter">所属行业</label>
        <select id="industry-filter" v-model="industry" data-testid="industry-filter">
          <option value="">全部行业</option>
          <option v-for="item in industries" :key="item" :value="item">{{ item }}</option>
        </select>
      </div>
      <button class="button reset-button" type="button" @click="resetFilters">重置条件</button>
    </div>
  </section>

  <section v-if="companies.length" class="panel directory-table">
    <header class="panel-header"><h2>查询结果</h2><p>点击公司名称或“进入分析”查看完整财务趋势与诊断。</p></header>
    <div class="table-scroll">
      <table>
        <caption class="sr-only">公司查询结果</caption>
        <thead><tr><th>公司</th><th>上市市场</th><th>所属行业</th><th>最新报告期</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="company in companies" :key="company.code">
            <td><RouterLink class="company-name" :to="`/company/${company.code}`"><strong>{{ company.name }}</strong><small>{{ company.code }}</small></RouterLink></td>
            <td>{{ marketLabel(company.market) }}</td>
            <td>{{ company.industryName ?? '未分类' }}</td>
            <td>{{ company.latestPeriod ?? '暂无数据' }}</td>
            <td><RouterLink class="entry-link" :to="`/company/${company.code}`">进入分析 <span aria-hidden="true">→</span></RouterLink></td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
  <EmptyState v-else title="没有匹配的公司" description="请调整公司名称、证券代码、市场或行业筛选条件。" />
</template>

<style scoped>
.directory-count { display: flex; align-items: baseline; gap: var(--space-xs); color: var(--color-ink-muted); font: var(--text-sm) var(--font-data); }
.directory-count strong { color: var(--color-accent); font-size: var(--text-2xl); letter-spacing: -.04em; }
.filter-panel { margin-bottom: var(--space-md); }
.toolbar { align-items: flex-end; }
.search-field { flex: 1 1 22rem; }
.field:not(.search-field) { min-width: 12rem; }
.reset-button { margin-left: auto; }
.directory-table .panel-header p { margin: 0; color: var(--color-ink-muted); font-size: var(--text-xs); }
.company-name { display: grid; justify-items: start; }
.company-name strong { font-family: var(--font-body); font-size: var(--text-sm); }
.company-name small { color: var(--color-ink-faint); font: var(--text-xs) var(--font-data); }
.company-name:hover strong, .entry-link { color: var(--color-accent); }
.entry-link { display: inline-flex; align-items: center; gap: var(--space-xs); font-family: var(--font-body); font-weight: 600; }
.entry-link span { transition: transform var(--dur-fast) var(--ease-out); }
.entry-link:hover span { transform: translateX(2px); }
tbody tr:hover { background: var(--color-paper-overlay); }
@media (max-width: 760px) { .field, .field:not(.search-field), .reset-button { width: 100%; } }
@media (prefers-reduced-motion: reduce) { .entry-link span { transition-duration: 0ms; } }
</style>

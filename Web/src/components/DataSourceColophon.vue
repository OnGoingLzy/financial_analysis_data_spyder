<script setup lang="ts">
import { useAnalysisStore } from '@/stores/analysis'
const store = useAnalysisStore()
</script>
<template>
  <footer class="colophon">
    <div><span>DATA SOURCE</span><strong>{{ store.meta?.databasePath ?? '正在连接指定数据库…' }}</strong></div>
    <div><span>LAST MODIFIED</span><strong>{{ store.meta ? new Date(store.meta.modifiedAt).toLocaleString('zh-CN') : '—' }}</strong></div>
    <div><span>COVERAGE</span><strong>{{ store.meta ? `${store.meta.companyCount} 家 · ${store.meta.periodStart} — ${store.meta.periodEnd}` : '—' }}</strong></div>
    <div><span>MODE</span><strong>SQLite / READ ONLY</strong></div>
  </footer>
</template>
<style scoped>
.colophon { display: grid; grid-template-columns: 2fr 1fr 1.2fr .8fr; gap: var(--space-lg); margin-top: var(--space-xl); padding: var(--space-md) 0; border-top: var(--rule-thin) solid var(--color-rule); color: var(--color-ink-muted); font-family: var(--font-data); }
.colophon div { min-width: 0; }.colophon span { display: block; color: var(--color-ink-faint); font-size: var(--text-xs); }.colophon strong { display: block; overflow: hidden; margin-top: var(--space-2xs); font-size: var(--text-xs); font-weight: 500; text-overflow: ellipsis; white-space: nowrap; }
@media (max-width: 760px) { .colophon { grid-template-columns: 1fr 1fr; } }
</style>

<script setup lang="ts">
import { onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import DataSourceColophon from '@/components/DataSourceColophon.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingState from '@/components/LoadingState.vue'
import { useAnalysisStore } from '@/stores/analysis'

const store = useAnalysisStore()
onMounted(() => store.initialize())
</script>
<template>
  <AppSidebar />
  <main class="workspace">
    <div class="topline"><span>企业财务深度分析</span><span>{{ new Date().toLocaleDateString('zh-CN') }} · 内部使用</span></div>
    <LoadingState v-if="store.loading && !store.meta" />
    <ErrorState v-else-if="store.error && !store.meta" :code="store.error.code" :message="store.error.message" @retry="store.initialize" />
    <RouterView v-else />
    <DataSourceColophon />
  </main>
</template>
<style scoped>
.workspace { min-height: 100vh; margin-left: 15rem; padding: 0 clamp(var(--space-md), 3vw, var(--space-2xl)) var(--space-xl); }
.topline { display: flex; justify-content: space-between; margin-bottom: var(--space-xl); padding: var(--space-md) 0; border-bottom: var(--rule-thin) solid var(--color-rule); color: var(--color-ink-faint); font: var(--text-xs) var(--font-data); letter-spacing: .05em; }
@media (max-width: 960px) { .workspace { margin-left: 0; } }
</style>

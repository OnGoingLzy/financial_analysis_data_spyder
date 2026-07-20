<script setup lang="ts">
defineProps<{ code: string; message: string }>()
defineEmits<{ retry: [] }>()
</script>

<template>
  <section class="error-state panel" role="alert">
    <div class="error-mark">!</div>
    <div>
      <p class="error-code">{{ code }}</p>
      <h2>{{ message }}</h2>
      <p>系统没有启用模拟数据回退。请检查数据库文件与标准化表后重试。</p>
      <button class="button" type="button" @click="$emit('retry')">重新读取数据库</button>
    </div>
  </section>
</template>

<style scoped>
.error-state { display: grid; grid-template-columns: auto 1fr; gap: var(--space-lg); padding: var(--space-xl); }
.error-mark { display: grid; place-items: center; width: 2.5rem; height: 2.5rem; border: var(--rule-thin) solid var(--color-warning); color: var(--color-warning); font: 700 var(--text-lg) var(--font-data); }
.error-code { margin-bottom: var(--space-xs); color: var(--color-warning); font: var(--text-xs) var(--font-data); }
.error-state h2 { margin-bottom: var(--space-xs); font-size: var(--text-lg); }
.error-state p:not(.error-code) { color: var(--color-ink-muted); }
</style>

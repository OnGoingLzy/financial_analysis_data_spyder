<script setup lang="ts">
defineProps<{ caption: string; columns: Array<{ key: string; label: string }>; rows: Array<Record<string, unknown>> }>()
</script>
<template>
  <div class="table-scroll"><table><caption class="sr-only">{{ caption }}</caption><thead><tr><th v-for="column in columns" :key="column.key">{{ column.label }}</th></tr></thead><tbody><tr v-for="(row, index) in rows" :key="index"><td v-for="column in columns" :key="column.key"><slot :name="column.key" :row="row">{{ row[column.key] ?? '暂无数据' }}</slot></td></tr></tbody></table></div>
</template>

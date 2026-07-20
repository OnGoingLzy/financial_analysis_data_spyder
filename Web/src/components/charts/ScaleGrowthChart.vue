<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from '@/charts/echarts'
import ChartPanel from '@/components/ChartPanel.vue'
const props = defineProps<{ rows: Array<{ name: string; value: number | null }>; title: string; description: string }>()
const option = computed<EChartsOption>(() => {
  const css = getComputedStyle(document.documentElement)
  return { animation: false, grid: { left: 96, right: 28, top: 24, bottom: 36 }, xAxis: { type: 'value', axisLabel: { color: css.getPropertyValue('--color-ink-muted') }, splitLine: { lineStyle: { color: css.getPropertyValue('--color-rule') } } }, yAxis: { type: 'category', data: props.rows.map((row) => row.name), axisLabel: { color: css.getPropertyValue('--color-ink-muted') }, axisLine: { show: false }, axisTick: { show: false } }, series: [{ type: 'bar', data: props.rows.map((row) => ({ value: row.value, itemStyle: { color: row.value != null && row.value < 0 ? css.getPropertyValue('--color-loss') : css.getPropertyValue('--color-profit') } })), barMaxWidth: 18 }] }
})
</script>
<template><ChartPanel :title="title" :description="description" :option="option"><table><caption>{{ title }}</caption><tbody><tr v-for="row in rows" :key="row.name"><th>{{ row.name }}</th><td>{{ row.value }}</td></tr></tbody></table></ChartPanel></template>

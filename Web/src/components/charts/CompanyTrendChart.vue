<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from '@/charts/echarts'
import ChartPanel from '@/components/ChartPanel.vue'
const props = defineProps<{ records: Array<{ reportPeriod: string; revenue: number | null; netProfit: number | null }>; title: string }>()
const option = computed<EChartsOption>(() => {
  const css = getComputedStyle(document.documentElement)
  return { animation: false, tooltip: { trigger: 'axis' }, legend: { data: ['营业收入', '净利润'], textStyle: { color: css.getPropertyValue('--color-ink-muted') } }, grid: { left: 72, right: 28, top: 48, bottom: 44 }, xAxis: { type: 'category', data: props.records.map((row) => row.reportPeriod), axisLabel: { color: css.getPropertyValue('--color-ink-muted'), rotate: props.records.length > 8 ? 30 : 0 } }, yAxis: { type: 'value', axisLabel: { color: css.getPropertyValue('--color-ink-muted'), formatter: (value: number) => `${(value / 100000000).toFixed(0)}亿` }, splitLine: { lineStyle: { color: css.getPropertyValue('--color-rule') } } }, series: [{ name: '营业收入', type: 'line', data: props.records.map((row) => row.revenue), showSymbol: false, lineStyle: { color: css.getPropertyValue('--color-accent') } }, { name: '净利润', type: 'line', data: props.records.map((row) => row.netProfit), showSymbol: false, lineStyle: { color: css.getPropertyValue('--color-profit') } }] }
})
</script>
<template><ChartPanel :title="title" description="金额单位：人民币元；悬停查看原始值" :option="option"><table><caption>{{ title }}</caption><tbody><tr v-for="row in records" :key="row.reportPeriod"><th>{{ row.reportPeriod }}</th><td>{{ row.revenue }}</td><td>{{ row.netProfit }}</td></tr></tbody></table></ChartPanel></template>

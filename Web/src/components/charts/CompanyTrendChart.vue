<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from '@/charts/echarts'
import { createTrendOption, readChartColors } from '@/charts/options'
import ChartPanel from '@/components/ChartPanel.vue'

const props = defineProps<{
  records: Array<{ reportPeriod: string; revenue: number | null; netProfit: number | null }>
  title: string
}>()
const option = computed<EChartsOption>(() => createTrendOption(props.records, readChartColors()))
</script>

<template>
  <ChartPanel :title="title" description="金额单位：人民币元；悬停查看原始值" :option="option">
    <table><caption>{{ title }}</caption><tbody><tr v-for="row in records" :key="row.reportPeriod"><th>{{ row.reportPeriod }}</th><td>{{ row.revenue }}</td><td>{{ row.netProfit }}</td></tr></tbody></table>
  </ChartPanel>
</template>

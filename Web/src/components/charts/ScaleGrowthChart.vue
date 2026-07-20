<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from '@/charts/echarts'
import { createBarOption, readChartColors } from '@/charts/options'
import ChartPanel from '@/components/ChartPanel.vue'
const props = defineProps<{ rows: Array<{ name: string; value: number | null }>; title: string; description: string }>()
const option = computed<EChartsOption>(() => createBarOption(props.rows, props.title, readChartColors()))
</script>
<template><ChartPanel :title="title" :description="description" :option="option"><table><caption>{{ title }}</caption><tbody><tr v-for="row in rows" :key="row.name"><th>{{ row.name }}</th><td>{{ row.value }}</td></tr></tbody></table></ChartPanel></template>

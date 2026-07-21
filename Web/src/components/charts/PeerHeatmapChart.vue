<script setup lang="ts">
import { computed } from 'vue'
import { createPeerHeatmapOption, readChartColors } from '@/charts/options'
import ChartPanel from '@/components/ChartPanel.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { CompareRow } from '@/types/financial'
const props = defineProps<{ rows: CompareRow[] }>()
const hasData = computed(() => props.rows.some((row) => Object.values(row.metrics).some((metric) => metric?.percentile != null)))
const option = computed(() => createPeerHeatmapOption(props.rows, readChartColors()))
</script>
<template><ChartPanel v-if="hasData" title="综合分位热力图" description="红色代表同行质量分位较高；风险指标已反向处理" :option="option" /><EmptyState v-else title="暂无综合分位" description="至少需要两家公司拥有可比较指标。" /></template>

<script setup lang="ts">
import { computed } from 'vue'
import { createGrowthProfitOption, readChartColors } from '@/charts/options'
import ChartPanel from '@/components/ChartPanel.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { CompareRow } from '@/types/financial'
const props = defineProps<{ rows: CompareRow[] }>()
const hasData = computed(() => props.rows.some((row) => row.profile.revenueYoyGrowth != null && row.profile.netMargin != null))
const option = computed(() => createGrowthProfitOption(props.rows, readChartColors()))
</script>
<template><ChartPanel v-if="hasData" title="增长—盈利矩阵" description="横轴营收增长，纵轴净利率，气泡面积代表营收规模" :option="option" /><EmptyState v-else title="暂无增长—盈利矩阵" description="需要营收同比和净利率数据。" /></template>

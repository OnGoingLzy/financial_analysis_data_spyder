<script setup lang="ts">
import { computed } from 'vue'
import { createCashRiskOption, readChartColors } from '@/charts/options'
import ChartPanel from '@/components/ChartPanel.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { CompareRow } from '@/types/financial'
const props = defineProps<{ rows: CompareRow[] }>()
const hasData = computed(() => props.rows.some((row) => row.profile.cashProfitRatio != null && row.profile.debtRatio != null))
const option = computed(() => createCashRiskOption(props.rows, readChartColors()))
</script>
<template><ChartPanel v-if="hasData" title="现金质量与偿债风险" description="横轴负债率，纵轴经营现金流/归母净利润；低于 1 使用绿色预警" :option="option" /><EmptyState v-else title="现金质量待补采" description="运行新版 Python 采集器补齐现金流量表后自动生成。" /></template>

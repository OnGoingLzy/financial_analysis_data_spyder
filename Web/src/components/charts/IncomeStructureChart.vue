<script setup lang="ts">
import { computed } from 'vue'
import { createIncomeStructureOption, readChartColors } from '@/charts/options'
import ChartPanel from '@/components/ChartPanel.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { CompareRow } from '@/types/financial'
const props = defineProps<{ rows: CompareRow[] }>()
const hasData = computed(() => props.rows.some((row) => row.profile.revenue != null))
const option = computed(() => createIncomeStructureOption(props.rows, readChartColors()))
</script>
<template><ChartPanel v-if="hasData" title="百元收入结构" description="各项金额占营业收入比例；负财务费用保留原始符号" :option="option" /><EmptyState v-else title="暂无收入结构" description="需要利润表收入和成本费用数据。" /></template>

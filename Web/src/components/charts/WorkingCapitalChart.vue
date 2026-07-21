<script setup lang="ts">
import { computed } from 'vue'
import { createWorkingCapitalOption, readChartColors } from '@/charts/options'
import ChartPanel from '@/components/ChartPanel.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { CompareRow } from '@/types/financial'
const props = defineProps<{ rows: CompareRow[] }>()
const hasData = computed(() => props.rows.some((row) => row.profile.cashConversionCycle != null))
const option = computed(() => createWorkingCapitalOption(props.rows, readChartColors()))
</script>
<template><ChartPanel v-if="hasData" title="营运效率与现金周期" description="应收天数 + 存货天数 − 应付天数；越短通常资金占用越低" :option="option" /><EmptyState v-else title="营运效率待补采" description="重新采集应收、存货、应付及期初余额后自动生成。" /></template>

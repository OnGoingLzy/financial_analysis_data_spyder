<script setup lang="ts">
import { computed } from 'vue'
import { formatAmount, formatNumber, formatPercent, metricTone, type MetricKind } from '@/utils/format'
const props = withDefaults(defineProps<{ value: number | null | undefined; format?: 'amount' | 'percent' | 'number'; kind?: MetricKind }>(), { format: 'amount', kind: 'profit' })
const text = computed(() => props.format === 'percent' ? formatPercent(props.value) : props.format === 'number' ? formatNumber(props.value) : formatAmount(props.value))
</script>
<template><span class="metric-number" :class="metricTone(value, kind)">{{ text }}</span></template>
<style scoped>.metric-number { font-family: var(--font-data); font-variant-numeric: tabular-nums; }</style>

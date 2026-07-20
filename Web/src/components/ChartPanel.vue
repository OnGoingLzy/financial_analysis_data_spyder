<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { init, type ECharts, type EChartsOption } from '@/charts/echarts'

const props = defineProps<{ title: string; description: string; option: EChartsOption }>()
const chartElement = ref<HTMLElement | null>(null)
let chart: ECharts | null = null

function render() { if (chart) chart.setOption(props.option, true) }
function resize() { chart?.resize() }
onMounted(() => { if (chartElement.value) { chart = init(chartElement.value); render(); window.addEventListener('resize', resize) } })
watch(() => props.option, render, { deep: true })
onBeforeUnmount(() => { window.removeEventListener('resize', resize); chart?.dispose() })
</script>
<template>
  <section class="panel chart-panel">
    <header class="panel-header"><div><h2>{{ title }}</h2><p>{{ description }}</p></div></header>
    <div ref="chartElement" class="chart" role="img" :aria-label="`${title}：${description}`"></div>
    <div class="sr-only"><slot /></div>
  </section>
</template>
<style scoped>.panel-header p { margin: var(--space-2xs) 0 0; color: var(--color-ink-muted); font-size: var(--text-xs); }.chart { height: 21rem; padding: var(--space-sm); }</style>

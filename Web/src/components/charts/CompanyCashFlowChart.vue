<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from '@/charts/echarts'
import { createCashFlowTrendOption, readChartColors } from '@/charts/options'
import ChartPanel from '@/components/ChartPanel.vue'
import type { AnalysisRecord } from '@/types/financial'

const props = defineProps<{ records: AnalysisRecord[] }>()
const option = computed<EChartsOption>(() => createCashFlowTrendOption(props.records, readChartColors()))
</script>

<template>
  <ChartPanel title="三类现金流趋势" description="金额单位：人民币元；悬停查看原始值" :option="option">
    <table>
      <caption>三类现金流趋势</caption>
      <tbody>
        <tr v-for="row in records" :key="row.reportPeriod">
          <th>{{ row.reportPeriod }}</th>
          <td>{{ row.cashFlow?.netOperatingCashFlow }}</td>
          <td>{{ row.cashFlow?.netInvestingCashFlow }}</td>
          <td>{{ row.cashFlow?.netFinancingCashFlow }}</td>
        </tr>
      </tbody>
    </table>
  </ChartPanel>
</template>

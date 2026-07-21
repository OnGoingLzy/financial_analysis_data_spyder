import { BarChart, HeatmapChart, LineChart, ScatterChart } from 'echarts/charts'
import { AriaComponent, GridComponent, LegendComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'

use([BarChart, HeatmapChart, LineChart, ScatterChart, AriaComponent, GridComponent, LegendComponent, TooltipComponent, VisualMapComponent, CanvasRenderer])

export { init } from 'echarts/core'
export type { ECharts, EChartsOption } from 'echarts'

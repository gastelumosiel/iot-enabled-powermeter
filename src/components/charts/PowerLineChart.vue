<script setup>
import { computed, ref } from 'vue'
import { BarChart3, CheckCircle2 } from 'lucide-vue-next'
import { useUiStore } from '../../stores/ui'

const props = defineProps({
  series: { type: Array, default: () => [] },
  value: { type: Number, default: 0 },
})

const width = 720
const height = 230
const pad = 28
const hoverIndex = ref(null)
const ui = useUiStore()

const allPoints = computed(() => props.series.flatMap((serie) => serie.points || []))
const max = computed(() => Math.max(...allPoints.value.map((point) => Number(point.power || 0)), 1))
const min = computed(() => Math.min(...allPoints.value.map((point) => Number(point.power || 0)), 0))
const firstSeries = computed(() => props.series[0]?.points || [])
const labelStep = computed(() => Math.max(1, Math.ceil(firstSeries.value.length / 6)))
const labels = computed(() => firstSeries.value.filter((_, index) => index % labelStep.value === 0))
const hoverX = computed(() => hoverIndex.value === null ? 0 : pad + (hoverIndex.value / Math.max(firstSeries.value.length - 1, 1)) * (width - pad * 2))
const hoverItems = computed(() => props.series.map((serie) => ({
  id: serie.id,
  name: serie.name,
  color: serie.color,
  point: serie.points?.[hoverIndex.value],
})).filter((item) => item.point))
const seriesKey = computed(() => props.series.map((serie) => `${serie.id}:${serie.points?.length || 0}`).join('|'))
const hoverXPercent = computed(() => hoverIndex.value === null ? 0 : (hoverX.value / width) * 100)
const hoverDots = computed(() => hoverItems.value.map((item) => ({
  ...item,
  x: hoverXPercent.value,
  y: (pointPosition(item.point, hoverIndex.value).y / height) * 100,
})))

function pointPosition(point, index) {
  const x = pad + (index / Math.max(firstSeries.value.length - 1, 1)) * (width - pad * 2)
  const normalized = (Number(point.power || 0) - min.value) / Math.max(max.value - min.value, 1)
  const y = height - pad - normalized * (height - pad * 2)
  return { x, y }
}

function buildPath(points = []) {
  return points.map((point, index) => {
    const { x, y } = pointPosition(point, index)
    return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
  }).join(' ')
}

function updateHover(event) {
  const rect = event.currentTarget.getBoundingClientRect()
  const ratio = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width))
  hoverIndex.value = Math.round(ratio * Math.max(firstSeries.value.length - 1, 0))
}
</script>

<template>
  <div class="clean-line-card">
    <div class="chart-toolbar">
      <span class="chart-chip">{{ ui.t('currentPeriod') }}</span>
      <span class="chart-icon"><BarChart3 :size="17" /></span>
    </div>
    <div class="chart-summary">
      <strong>{{ Math.round(value).toLocaleString(ui.language === 'ES' ? 'es-MX' : 'en-US') }} W</strong>
      <span>{{ ui.t('periodAverage') }}</span>
      <small><CheckCircle2 :size="14" /> {{ ui.t('operatingRange') }}</small>
    </div>
    <Transition name="chart-soft" appear>
      <div v-if="series.length" :key="seriesKey" class="chart-stage">
    <div class="chart-legend">
      <span v-for="serie in series" :key="serie.id"><i :style="{ background: serie.color }"></i>{{ serie.name }}</span>
    </div>
    <div class="chart-plot">
      <svg
        viewBox="0 0 720 230"
        preserveAspectRatio="none"
        class="clean-line-svg"
        @mousemove="updateHover"
        @mouseleave="hoverIndex = null"
      >
        <defs>
          <linearGradient id="cleanLineGlow" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stop-color="#10b981" stop-opacity=".18" />
            <stop offset="1" stop-color="#10b981" stop-opacity="0" />
          </linearGradient>
        </defs>
        <path
          v-if="series[0]"
          :d="`${buildPath(series[0].points)} L ${width - pad} ${height - pad} L ${pad} ${height - pad} Z`"
          fill="url(#cleanLineGlow)"
        />
        <path
          v-for="serie in series"
          :key="serie.id"
          :d="buildPath(serie.points)"
          fill="none"
          :stroke="serie.color"
          stroke-width="4"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <g v-if="hoverIndex !== null">
          <line :x1="hoverX" y1="12" :x2="hoverX" :y2="height - 16" stroke="#94a3b8" stroke-width="1" opacity=".55" />
        </g>
      </svg>
      <span
        v-for="dot in hoverDots"
        :key="dot.id"
        class="chart-hover-dot"
        :style="{ left: `${dot.x}%`, top: `${dot.y}%`, borderColor: dot.color }"
      ></span>
    </div>
    <div v-if="hoverIndex !== null && hoverItems.length" class="chart-tooltip" :style="{ left: `${Math.min(78, Math.max(28, (hoverX / width) * 100))}%` }">
      <strong>{{ hoverItems[0].point.label }}</strong>
      <span v-for="item in hoverItems" :key="item.id"><i :style="{ background: item.color }"></i>{{ item.name }}: {{ item.point.power }} W</span>
    </div>
    <div class="chart-labels">
      <span v-for="point in labels" :key="point.label">{{ point.label }}</span>
    </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { BarChart3, CheckCircle2 } from 'lucide-vue-next'
import { useUiStore } from '../../stores/ui'

const props = defineProps({
  series: { type: Array, default: () => [] },
  value: { type: Number, default: 0 },
  unit: { type: String, default: 'W' },
  metricLabel: { type: String, default: '' },
})

const width = 720
const height = 230
const pad = 28
const hoverIndex = ref(null)
const tooltipRef = ref(null)
const ui = useUiStore()

const allPoints = computed(() => props.series.flatMap((serie) => serie.points || []))
const max = computed(() => Math.max(...allPoints.value.map((point) => pointValue(point)), 1))
const min = computed(() => Math.min(...allPoints.value.map((point) => pointValue(point)), 0))
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
const seriesKey = computed(() => [
  props.metricLabel,
  props.unit,
  props.series.map((serie) => `${serie.id}:${serie.points?.length || 0}`).join('|'),
].join('|'))
const hoverXPercent = computed(() => hoverIndex.value === null ? 0 : (hoverX.value / width) * 100)
const hoverDots = computed(() => hoverItems.value.map((item) => ({
  ...item,
  x: hoverXPercent.value,
  y: (pointPosition(item.point, hoverIndex.value).y / height) * 100,
})))
const tooltipStyle = computed(() => ({
  maxHeight: `${props.series.length > 12 ? 128 : 128}px`,
}))

function pointPosition(point, index) {
  const x = pad + (index / Math.max(firstSeries.value.length - 1, 1)) * (width - pad * 2)
  const normalized = (pointValue(point) - min.value) / Math.max(max.value - min.value, 1)
  const y = height - pad - normalized * (height - pad * 2)
  return { x, y }
}

function pointValue(point) {
  return Number(point?.value ?? point?.power ?? 0)
}

function formatValue(value) {
  return Number(value || 0).toLocaleString(ui.language === 'ES' ? 'es-MX' : 'en-US', { maximumFractionDigits: props.unit === 'W' || props.unit === 'VAR' || props.unit === 'VA' ? 0 : 2 })
}

function shortName(name = '') {
  const clean = String(name)
  return clean.length > 15 ? `${clean.slice(0, 15)}...` : clean
}

function buildPath(points = []) {
  return points.map((point, index) => {
    const { x, y } = pointPosition(point, index)
    return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
  }).join(' ')
}

function buildRibbonPath(points = []) {
  if (!points.length) return ''
  const top = points.map((point, index) => {
    const { x, y } = pointPosition(point, index)
    return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
  }).join(' ')
  const first = pointPosition(points[0], 0)
  const last = pointPosition(points[points.length - 1], points.length - 1)
  return `${top} L ${last.x.toFixed(2)} ${height - pad} L ${first.x.toFixed(2)} ${height - pad} Z`
}

function updateHover(event) {
  const rect = event.currentTarget.getBoundingClientRect()
  const viewX = ((event.clientX - rect.left) / rect.width) * width
  const ratio = Math.min(1, Math.max(0, (viewX - pad) / (width - pad * 2)))
  hoverIndex.value = Math.round(ratio * Math.max(firstSeries.value.length - 1, 0))
}

function clearHover() {
  hoverIndex.value = null
}

function scrollTooltip(event) {
  const tooltip = tooltipRef.value
  if (!tooltip || hoverIndex.value === null || tooltip.scrollHeight <= tooltip.clientHeight) return
  event.preventDefault()
  tooltip.scrollTop += event.deltaY
}
</script>

<template>
  <div class="clean-line-card">
    <div class="chart-toolbar">
      <span class="chart-chip">{{ metricLabel || ui.t('currentPeriod') }}</span>
      <span class="chart-icon"><BarChart3 :size="17" /></span>
    </div>
    <div class="chart-summary">
      <strong>{{ formatValue(value) }} {{ unit }}</strong>
      <span>{{ ui.t('periodAverage') }}</span>
      <small><CheckCircle2 :size="14" /> {{ ui.t('operatingRange') }}</small>
    </div>
    <Transition name="chart-soft" appear>
      <div v-if="series.length" :key="seriesKey" class="chart-stage" @mouseleave="clearHover">
    <div class="chart-plot">
      <svg
        viewBox="0 0 720 230"
        preserveAspectRatio="none"
        class="clean-line-svg"
      >
        <path
          v-for="serie in series"
          :key="`ribbon-${serie.id}`"
          :d="buildRibbonPath(serie.points)"
          :fill="serie.color"
          class="chart-area-ribbon"
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
      <div class="chart-hit-area" @mousemove="updateHover" @wheel="scrollTooltip"></div>
      <span
        v-for="dot in hoverDots"
        :key="dot.id"
        class="chart-hover-dot"
        :style="{ left: `${dot.x}%`, top: `${dot.y}%`, borderColor: dot.color }"
      ></span>
    </div>
    <Transition name="popup-fade">
      <div ref="tooltipRef" v-if="hoverIndex !== null && hoverItems.length" class="chart-tooltip" :class="{ dense: hoverItems.length > 10 }" :style="tooltipStyle" @mouseenter.stop @mousemove.stop @wheel.stop>
        <strong>{{ hoverItems[0].point.label }}</strong>
        <span v-for="item in hoverItems" :key="item.id">
          <i :style="{ background: item.color }"></i>
          <b :title="item.name">{{ shortName(item.name) }}:</b>
          <em>{{ formatValue(item.point.value ?? item.point.power) }} {{ unit }}</em>
        </span>
      </div>
    </Transition>
    <div class="chart-labels">
      <span v-for="point in labels" :key="point.label">{{ point.label }}</span>
    </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useDeviceStore } from '../stores/devices'
import { useUiStore } from '../stores/ui'
import { makeDeviceHistorySeries } from '../mocks/devices'
import { analyticsService } from '../services/analyticsService'
import PowerLineChart from '../components/charts/PowerLineChart.vue'
import DeviceBarChart from '../components/charts/DeviceBarChart.vue'

const devices = useDeviceStore()
const ui = useUiStore()
const selectedDeviceIds = ref([])
const range = ref('24h')
const parameter = ref('active_power')
const series = ref([])
const maxAgeSeconds = ref(0)
let timer

const chartPalette = [
  '#0f766e',
  '#2563eb',
  '#7c3aed',
  '#dc2626',
  '#ea580c',
  '#0891b2',
  '#65a30d',
  '#9333ea',
  '#be123c',
  '#0284c7',
  '#ca8a04',
  '#0d9488',
  '#4f46e5',
  '#db2777',
  '#16a34a',
  '#b45309',
  '#0369a1',
  '#a21caf',
  '#15803d',
  '#c2410c',
]

const ranges = [
  { value: '1h', label: 'lastHour', seconds: 60 * 60 },
  { value: '8h', label: 'last8h', seconds: 8 * 60 * 60 },
  { value: '24h', label: 'last24h', seconds: 24 * 60 * 60 },
  { value: '7d', label: 'sevenDays', seconds: 7 * 24 * 60 * 60 },
  { value: '30d', label: 'thirtyDays', seconds: 30 * 24 * 60 * 60 },
  { value: '3m', label: 'threeMonths', seconds: 90 * 24 * 60 * 60 },
  { value: '6m', label: 'sixMonths', seconds: 180 * 24 * 60 * 60 },
  { value: '12m', label: 'twelveMonths', seconds: 365 * 24 * 60 * 60 },
]

const parameters = [
  { value: 'active_power', label: 'activePower', unit: 'W' },
  { value: 'reactive_power', label: 'reactivePower', unit: 'VAR' },
  { value: 'apparent_power', label: 'apparentPower', unit: 'VA' },
  { value: 'vrms', label: 'lineVoltage', unit: 'V' },
  { value: 'irms', label: 'lineCurrent', unit: 'A' },
  { value: 'power_factor', label: 'powerFactor', unit: 'PF' },
  { value: 'frequency', label: 'frequency', unit: 'Hz' },
  { value: 'phase', label: 'phase', unit: '°' },
]

const selectedParameter = computed(() => parameters.find((item) => item.value === parameter.value) || parameters[0])
const selectedParameterUnit = computed(() => parameterUnit(selectedParameter.value))
const flattenedPoints = computed(() => series.value.flatMap((serie) => serie.points || []))
const devicePeriodAverages = computed(() => series.value.map((serie) => {
  const points = serie.points || []
  const average = points.reduce((sum, point) => sum + Number(point.value ?? point.power ?? 0), 0) / Math.max(points.length, 1)
  const device = visibleDevices.value.find((item) => item.device_id === serie.id)
  return { ...(device || {}), device_id: serie.id, name: serie.name, color: serie.color, average_value: average, active_power: average }
}))
const selectedPeriodTotal = computed(() => devicePeriodAverages.value.reduce((sum, device) => sum + Number(device.average_value || 0), 0))
const visibleDevices = computed(() => devices.devices.filter((device) => selectedDeviceIds.value.includes(device.device_id)))
const allSelected = computed(() => devices.devices.length > 0 && selectedDeviceIds.value.length === devices.devices.length)
const availableRanges = computed(() => {
  if (!maxAgeSeconds.value) return ranges.slice(0, 1)
  const options = ranges.filter((option) => option.seconds <= maxAgeSeconds.value)
  return options.length ? options : ranges.slice(0, 1)
})

function clampRange() {
  if (!availableRanges.value.some((option) => option.value === range.value)) {
    range.value = availableRanges.value[availableRanges.value.length - 1]?.value || '1h'
  }
}

async function loadAvailability() {
  const data = await analyticsService.availability({ device_ids: selectedDeviceIds.value.join(',') })
  maxAgeSeconds.value = Number(data?.max_age_seconds || 0)
  clampRange()
}

async function loadAnalytics() {
  clampRange()
  series.value = makeDeviceHistorySeries(visibleDevices.value, range.value, ui.language === 'ES' ? 'es-MX' : 'en-US', parameter.value)
    .map((serie, index) => ({ ...serie, color: chartPalette[index % chartPalette.length] }))
}

function parameterUnit(option) {
  return option.value === 'phase' ? '°' : option.unit
}

function optionWithUnit(option) {
  return `${ui.t(option.label)} (${parameterUnit(option)})`
}

function toggleDevice(id) {
  selectedDeviceIds.value = selectedDeviceIds.value.includes(id)
    ? selectedDeviceIds.value.filter((item) => item !== id)
    : [...selectedDeviceIds.value, id]
}

function selectAllDevices() {
  selectedDeviceIds.value = allSelected.value ? [] : devices.devices.map((device) => device.device_id)
}

onMounted(async () => {
  await devices.fetchDevices()
  selectedDeviceIds.value = devices.devices.map((device) => device.device_id)
  await loadAvailability()
  await loadAnalytics()
  timer = setInterval(async () => {
    await devices.fetchDevices()
    await loadAvailability()
    await loadAnalytics()
  }, 9000)
})
onUnmounted(() => clearInterval(timer))

watch([range, parameter, () => ui.language, () => selectedDeviceIds.value.join('|')], async () => {
  await loadAvailability()
  await loadAnalytics()
})
watch(maxAgeSeconds, clampRange)
watch(() => devices.devices.map((device) => device.device_id).join('|'), () => {
  if (!selectedDeviceIds.value.length) selectedDeviceIds.value = devices.devices.map((device) => device.device_id)
  selectedDeviceIds.value = selectedDeviceIds.value.filter((id) => devices.devices.some((device) => device.device_id === id))
})
</script>

<template>
  <section>
    <div class="page-header">
      <div><h1>{{ ui.t('analyticsTitle') }}</h1><p>{{ ui.t('analyticsSubtitle') }}</p></div>
    </div>
    <div class="card analytics-card">
      <h2>{{ ui.t('usageHistory') }}</h2>
      <div class="filters">
        <div class="field"><label>{{ ui.t('timeRange') }}</label><select v-model="range" class="select"><option v-for="option in availableRanges" :key="option.value" :value="option.value">{{ ui.t(option.label) }}</option></select></div>
        <div class="field"><label>{{ ui.t('metricParameter') }}</label><select v-model="parameter" class="select"><option v-for="option in parameters" :key="option.value" :value="option.value">{{ optionWithUnit(option) }}</option></select></div>
      </div>
      <div class="device-selector">
        <button type="button" class="device-filter-chip" :class="{ selected: allSelected }" @click="selectAllDevices">{{ ui.t('selectAll') }}</button>
        <button
          v-for="device in devices.devices"
          :key="device.device_id"
          type="button"
          class="device-filter-chip"
          :class="{ selected: selectedDeviceIds.includes(device.device_id) }"
          @click="toggleDevice(device.device_id)"
        >
          {{ device.name }}
        </button>
      </div>
      <div class="chart-box chart-box-clean"><PowerLineChart :series="series" :value="selectedPeriodTotal" :unit="selectedParameterUnit" :metric-label="ui.t(selectedParameter.label)" /></div>
    </div>
    <div class="grid analytics-grid analytics-grid-single">
      <div class="card analytics-card analytics-wide-card">
        <h2>{{ ui.t('deviceUsage') }}</h2>
        <div class="chart-box chart-box-clean" style="min-height:300px"><DeviceBarChart :devices="devicePeriodAverages" metric="average_value" :unit="selectedParameterUnit" /></div>
      </div>
    </div>
  </section>
</template>

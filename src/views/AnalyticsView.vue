<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useDeviceStore } from '../stores/devices'
import { useUiStore } from '../stores/ui'
import { analyticsService } from '../services/analyticsService'
import { makeDeviceHistorySeries } from '../mocks/devices'
import PowerLineChart from '../components/charts/PowerLineChart.vue'
import DeviceBarChart from '../components/charts/DeviceBarChart.vue'
import CfeSummaryCard from '../components/cards/CfeSummaryCard.vue'

const devices = useDeviceStore()
const ui = useUiStore()
const selectedDevice = ref('all')
const range = ref('24h')
const series = ref([])
const cfe = ref({ accumulated_kwh: 0, configured_limit: 0, usage_percent: 0, remaining_kwh: 0 })

const flattenedPoints = computed(() => series.value.flatMap((serie) => serie.points || []))
const average24h = computed(() => Math.round(flattenedPoints.value.reduce((sum, point) => sum + point.power, 0) / Math.max(flattenedPoints.value.length, 1)))
const monthlyEstimate = computed(() => ((devices.totalPower / 1000) * 24 * 30).toFixed(1))
const visibleDevices = computed(() => selectedDevice.value === 'all'
  ? devices.devices
  : devices.devices.filter((device) => device.device_id === selectedDevice.value)
)

async function loadAnalytics() {
  series.value = makeDeviceHistorySeries(visibleDevices.value, range.value, ui.language === 'ES' ? 'es-MX' : 'en-US')
  cfe.value = await analyticsService.cfeSummary()
}

onMounted(async () => {
  await devices.fetchDevices()
  await loadAnalytics()
})
watch([selectedDevice, range, () => ui.language], loadAnalytics)
</script>

<template>
  <section>
    <div class="page-header">
      <div><h1>{{ ui.t('analyticsTitle') }}</h1><p>{{ ui.t('analyticsSubtitle') }}</p></div>
    </div>
    <div class="card analytics-card">
      <h2>{{ ui.t('usageHistory') }}</h2>
      <div class="filters">
        <div class="field"><label>{{ ui.t('device') }}</label><select v-model="selectedDevice" class="select"><option value="all">{{ ui.t('allDevices') }}</option><option v-for="device in devices.devices" :key="device.device_id" :value="device.device_id">{{ device.name }}</option></select></div>
        <div class="field"><label>{{ ui.t('timeRange') }}</label><select v-model="range" class="select"><option value="24h">{{ ui.t('last24h') }}</option><option value="7d">{{ ui.t('sevenDays') }}</option><option value="30d">{{ ui.t('thirtyDays') }}</option></select></div>
      </div>
      <div class="chart-box chart-box-clean"><PowerLineChart :series="series" :value="average24h" /></div>
    </div>
    <div class="grid analytics-grid">
      <div class="card analytics-card">
        <h2>{{ ui.t('deviceUsage') }}</h2>
        <div class="chart-box chart-box-clean" style="min-height:300px"><DeviceBarChart :devices="devices.devices" /></div>
      </div>
      <div class="card analytics-card">
        <h2>{{ ui.t('generalStats') }}</h2>
        <div class="stat-stack">
          <div class="stat-card stat-green"><span>{{ ui.t('currentTotal') }}</span><strong>{{ Math.round(devices.totalPower) }} W</strong></div>
          <div class="stat-card stat-blue"><span>{{ ui.t('average24h') }}</span><strong>{{ average24h }} W</strong></div>
          <div class="stat-card stat-purple"><span>{{ ui.t('activeDevicesLabel') }}</span><strong>{{ devices.activeCount }} {{ ui.t('of') }} {{ devices.devices.length }}</strong></div>
          <div class="stat-card stat-yellow"><span>{{ ui.t('monthlyEstimate') }}</span><strong>{{ monthlyEstimate }} kWh</strong></div>
          <CfeSummaryCard :summary="cfe" />
        </div>
      </div>
    </div>
  </section>
</template>

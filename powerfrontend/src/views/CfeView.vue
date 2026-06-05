<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { CalendarDays, ExternalLink, Save, WalletCards } from 'lucide-vue-next'
import { useDeviceStore } from '../stores/devices'
import { useUiStore } from '../stores/ui'
import { cfeService } from '../services/cfeService'
import { analyticsService } from '../services/analyticsService'
import { userService } from '../services/userService'
import DeviceIcon from '../components/devices/DeviceIcon.vue'
import { DATA_REFRESH_MS } from '../config/refresh'

const devices = useDeviceStore()
const ui = useUiStore()
const today = new Date().toISOString().slice(0, 10)
const savedSettings = ref({
  rate: 'domestic_1c',
  periodStart: today,
})
const form = ref({
  ...savedSettings.value,
})
const tariffOptions = cfeService.tariffOptions()
const tariff = ref(cfeService.localTariff(savedSettings.value.rate))
const cfeSummary = ref({ accumulated_kwh: 0, devices: [] })
const saveMessage = ref(false)
let saveMessageTimer
let dataTimer

const selectedTariffOption = computed(() => tariffOptions.find((option) => option.value === savedSettings.value.rate) || tariffOptions[0])
const totalKwh = computed(() => Number(cfeSummary.value.accumulated_kwh || 0))
const monthlyLimit = computed(() => Number(tariff.value?.monthlyLimit || 0))
const currentPeriod = computed(() => getCurrentBillingPeriod(savedSettings.value.periodStart))
const currentBillingMonth = computed(() => getCurrentBillingMonth(currentPeriod.value))
const elapsedBillingMonths = computed(() => currentBillingMonth.value.index)
const currentMonthKwh = computed(() => totalKwh.value / Math.max(elapsedBillingMonths.value, 1))
const usagePercent = computed(() => Math.min(100, (currentMonthKwh.value / Math.max(monthlyLimit.value, 1)) * 100))
const remainingKwh = computed(() => Math.max(0, monthlyLimit.value - currentMonthKwh.value))
const daysLeft = computed(() => Math.max(0, Math.ceil((currentPeriod.value.end - new Date()) / 86400000)))
const tierResult = computed(() => calculateTieredCost(totalKwh.value, tariff.value?.blocks || [], elapsedBillingMonths.value))
const currentMonthTier = computed(() => calculateTieredCost(currentMonthKwh.value, tariff.value?.blocks || [], 1).currentBlock)
const currentKwhPrice = computed(() => currentMonthTier.value?.price || 0)
const currentMargin = computed(() => {
  const current = currentMonthTier.value
  if (!current || !Number.isFinite(current.remaining)) return ui.t('excessTierActive')
  return `${current.remaining.toFixed(1)} kWh ${ui.t('beforeNextTier')}`
})
const deviceCosts = computed(() => (cfeSummary.value.devices || []).map((summaryDevice) => {
  const device = devices.devices.find((item) => item.device_id === summaryDevice.device_id) || {}
  const energyKwh = Number(summaryDevice.energy_kwh || 0)
  return {
    ...device,
    ...summaryDevice,
    icon: device.icon || 'plug',
    energy_kwh: energyKwh,
    cost: calculateTieredCost(energyKwh, tariff.value?.blocks || [], elapsedBillingMonths.value).total,
  }
}))
const meterSegments = computed(() => buildMeterSegments(tariff.value?.blocks || [], monthlyLimit.value))
const pointerStyle = computed(() => ({ left: `${usagePercent.value}%` }))

function addMonths(date, months) {
  const result = new Date(date)
  const day = result.getDate()
  result.setMonth(result.getMonth() + months)
  if (result.getDate() < day) result.setDate(0)
  return result
}

function getCurrentBillingPeriod(startValue) {
  const start = new Date(`${startValue || today}T00:00:00`)
  if (Number.isNaN(start.getTime())) return { start: new Date(`${today}T00:00:00`), end: addMonths(new Date(`${today}T00:00:00`), 2) }
  const now = new Date()
  let periodStart = start
  let periodEnd = addMonths(periodStart, 2)
  while (periodEnd <= now) {
    periodStart = periodEnd
    periodEnd = addMonths(periodStart, 2)
  }
  return { start: periodStart, end: periodEnd }
}

function getCurrentBillingMonth(period) {
  const now = new Date()
  const secondMonthStart = addMonths(period.start, 1)
  const inSecondMonth = now >= secondMonthStart
  return {
    index: inSecondMonth ? 2 : 1,
    start: inSecondMonth ? secondMonthStart : period.start,
    end: inSecondMonth ? period.end : secondMonthStart,
  }
}

function buildMeterSegments(blocks, limit) {
  const finiteBlocks = blocks.filter((block) => Number.isFinite(block.kwh))
  const usedFinite = finiteBlocks.reduce((sum, block) => sum + Number(block.kwh || 0), 0)
  const excessKwh = Math.max(0, Number(limit || 0) - usedFinite)
  const normalized = [
    ...finiteBlocks,
    { key: 'excess', kwh: excessKwh },
  ]
  return normalized.map((block) => ({
    key: block.key,
    width: `${Math.max(0, (Number(block.kwh || 0) / Math.max(limit, 1)) * 100)}%`,
  }))
}

function calculateTieredCost(kwh, blocks, months = 1) {
  let remaining = Number(kwh || 0)
  let total = 0
  let consumedBefore = 0
  let currentBlock = null
  const breakdown = blocks.map((block) => {
    const blockKwh = Number.isFinite(block.kwh) ? block.kwh * Math.max(months, 1) : Infinity
    const used = Math.max(0, Math.min(remaining, blockKwh))
    remaining -= used
    total += used * Number(block.price || 0)
    const blockStart = consumedBefore
    consumedBefore += Number.isFinite(blockKwh) ? blockKwh : 0
    if (!currentBlock && kwh >= blockStart && (kwh <= consumedBefore || !Number.isFinite(blockKwh))) {
      currentBlock = {
        key: block.key,
        price: Number(block.price || 0),
        remaining: Number.isFinite(blockKwh) ? Math.max(0, consumedBefore - kwh) : Infinity,
      }
    }
    return { ...block, used }
  })
  return { total, breakdown, currentBlock }
}

function money(value) {
  return Number(value || 0).toLocaleString(ui.language === 'ES' ? 'es-MX' : 'en-US', { style: 'currency', currency: 'MXN' })
}

function dateLabel(value) {
  return value.toLocaleDateString(ui.language === 'ES' ? 'es-MX' : 'en-US', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function saveSettings() {
  const data = await userService.updateCfeSettings({
    rate: form.value.rate,
    period_start: form.value.periodStart,
  })
  form.value = {
    rate: data.rate || form.value.rate,
    periodStart: data.period_start || form.value.periodStart,
  }
  savedSettings.value = { ...form.value }
  saveMessage.value = true
  clearTimeout(saveMessageTimer)
  saveMessageTimer = window.setTimeout(() => {
    saveMessage.value = false
  }, 2200)
  window.dispatchEvent(new CustomEvent('powerlytix:cfe-settings-saved', { detail: { ...savedSettings.value } }))
  await loadTariff()
  await loadCfeSummary()
}

async function loadTariff() {
  tariff.value = cfeService.localTariff(savedSettings.value.rate)
  tariff.value = await cfeService.tariff({ tariff: savedSettings.value.rate, periodStart: currentBillingMonth.value.start.toISOString().slice(0, 10) })
}

async function loadUserCfeSettings() {
  const data = await userService.cfeSettings()
  savedSettings.value = {
    rate: data.rate || savedSettings.value.rate,
    periodStart: data.period_start || savedSettings.value.periodStart,
  }
  form.value = { ...savedSettings.value }
}

async function loadCfeSummary() {
  cfeSummary.value = await analyticsService.cfeSummary({
    period_start: currentPeriod.value.start.toISOString().slice(0, 10),
    period_end: currentPeriod.value.end.toISOString().slice(0, 10),
    configured_limit: monthlyLimit.value * Math.max(elapsedBillingMonths.value, 1),
  })
}

onMounted(async () => {
  await loadUserCfeSettings()
  await devices.fetchDevices()
  await loadTariff()
  await loadCfeSummary()
  dataTimer = setInterval(async () => {
    await devices.fetchDevices()
    await loadCfeSummary()
  }, DATA_REFRESH_MS)
})

onUnmounted(() => {
  clearTimeout(saveMessageTimer)
  clearInterval(dataTimer)
})

</script>

<template>
  <section>
    <div class="page-header">
      <div><h1>{{ ui.t('cfeTitle') }}</h1><p>{{ ui.t('cfeSubtitle') }}</p></div>
    </div>

    <div class="grid cfe-grid">
      <div class="card analytics-card cfe-meter-card">
        <div class="meter-head">
          <span class="icon-box"><WalletCards :size="20" /></span>
          <div>
            <h2>{{ ui.t('estimatedCost') }}</h2>
            <strong>{{ money(tierResult.total) }}</strong>
          </div>
        </div>
        <div class="cfe-semaphore">
          <span v-for="segment in meterSegments" :key="segment.key" :class="segment.key" :style="{ width: segment.width }"></span>
          <i :style="pointerStyle"></i>
        </div>
        <div class="meter-meta">
          <span>{{ currentMonthKwh.toFixed(2) }} kWh {{ ui.t('monthlyConsumption') }}</span>
          <span>{{ remainingKwh.toFixed(1) }} kWh {{ ui.t('remaining') }}</span>
        </div>
        <div class="tier-margin">
          <span>{{ ui.t('currentConsumptionMargin') }}</span>
          <strong>{{ ui.t(currentMonthTier?.key || 'basic') }} - {{ money(currentKwhPrice) }}/kWh</strong>
          <small>{{ currentMargin }}</small>
        </div>
      </div>
      <div class="card analytics-card">
        <h2>{{ ui.t('cfeSettings') }}</h2>
        <div class="filters compact-filters">
          <div class="field">
            <label>{{ ui.t('cfeRate') }}</label>
            <select v-model="form.rate" class="select">
              <option v-for="option in tariffOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </div>
          <div class="field">
            <label>{{ ui.t('receiptPeriodStart') }}</label>
            <input v-model="form.periodStart" class="input" type="date" />
          </div>
        </div>
        <div class="period-summary">
          <CalendarDays :size="18" />
          <span>{{ dateLabel(currentPeriod.start) }} - {{ dateLabel(currentPeriod.end) }}</span>
          <strong>{{ ui.t('billingMonth') }} {{ currentBillingMonth.index }} - {{ daysLeft }} {{ ui.t('daysRemaining') }}</strong>
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-primary" @click="saveSettings"><Save :size="18" /> {{ ui.t('save') }}</button>
          <Transition name="popup-fade">
            <span v-if="saveMessage" class="save-status">{{ ui.t('savedSuccessfully') }}</span>
          </Transition>
          <a class="btn btn-secondary" :href="tariff?.sourceUrl || selectedTariffOption.sourceUrl" target="_blank" rel="noreferrer"><ExternalLink :size="18" /> {{ ui.t('officialCfeSource') }}</a>
        </div>
      </div>
    </div>

    <div class="grid cfe-grid cfe-wide-grid">
      <div class="card analytics-card">
        <h2>{{ ui.t('costByDevice') }}</h2>
        <div class="cost-list">
          <div v-for="device in deviceCosts" :key="device.device_id" class="cost-row">
            <div class="cost-device">
              <span class="mini-device-icon"><DeviceIcon :icon="device.icon" :size="16" /></span>
              <div>
              <strong>{{ device.name }}</strong>
              <span>{{ Number(device.energy_kwh || 0).toFixed(2) }} kWh</span>
              </div>
            </div>
            <strong>{{ money(device.cost) }}</strong>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

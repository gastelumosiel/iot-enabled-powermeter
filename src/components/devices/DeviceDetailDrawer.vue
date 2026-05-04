<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { Activity, X } from 'lucide-vue-next'
import StatusBadge from '../ui/StatusBadge.vue'
import DeviceIcon from './DeviceIcon.vue'
import { deviceService } from '../../services/deviceService'
import { useUiStore } from '../../stores/ui'

const props = defineProps({ device: { type: Object, default: null } })
const emit = defineEmits(['close', 'updated'])
const ui = useUiStore()
const liveDevice = ref(props.device)
const isVisible = ref(Boolean(props.device))
let requestToken = 0
let timer
let closeTimer

const deviceId = computed(() => liveDevice.value?.device_id || liveDevice.value?.id)

function formatTime(value) {
  return value ? new Date(value).toLocaleTimeString(ui.language === 'ES' ? 'es-MX' : 'en-US') : ui.t('noData')
}

async function refresh() {
  if (!isVisible.value || !deviceId.value) return
  const token = ++requestToken
  const expectedId = deviceId.value
  const data = await deviceService.getById(deviceId.value)
  if (data && isVisible.value && token === requestToken && (data.device_id === expectedId || data.id === expectedId)) {
    liveDevice.value = data
    emit('updated', data)
  }
}

function closeDrawer() {
  isVisible.value = false
  requestToken += 1
  clearTimeout(closeTimer)
  closeTimer = window.setTimeout(() => {
    liveDevice.value = null
    emit('close')
  }, 220)
}

watch(() => props.device, (value) => {
  requestToken += 1
  clearTimeout(closeTimer)
  if (value) {
    liveDevice.value = value
    isVisible.value = true
  } else {
    isVisible.value = false
  }
}, { immediate: true })

onMounted(() => {
  timer = setInterval(refresh, 10000)
})

onUnmounted(() => {
  clearInterval(timer)
  clearTimeout(closeTimer)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer-overlay-fade">
      <div v-if="isVisible" class="drawer-overlay" @click="closeDrawer"></div>
    </Transition>
    <Transition name="drawer-slide">
      <aside v-if="isVisible && liveDevice" class="drawer" :aria-label="ui.t('detailLabel')">
        <div class="drawer-top">
          <div class="drawer-title">
            <span class="icon-box"><DeviceIcon :icon="liveDevice.icon" :size="28" /></span>
            <div>
              <h2>{{ liveDevice.name }}</h2>
              <span class="muted">{{ ui.t('deviceId') }}: {{ liveDevice.device_id }}</span>
            </div>
          </div>
          <button class="icon-btn" :aria-label="ui.t('closeDetail')" @click="closeDrawer"><X :size="20" /></button>
        </div>

        <section class="card detail-section">
          <div class="metric-grid">
            <div class="metric"><span>{{ ui.t('activePower') }} (P)</span><strong>{{ Math.round(liveDevice.active_power) }} W</strong></div>
            <div class="metric purple"><span>{{ ui.t('reactivePower') }} (Q)</span><strong>{{ liveDevice.reactive_power }} VAR</strong></div>
            <div class="metric blue"><span>{{ ui.t('apparentPower') }} (S)</span><strong>{{ liveDevice.apparent_power }} VA</strong></div>
            <div class="metric yellow"><span>{{ ui.t('powerFactor') }} (PF)</span><strong>{{ liveDevice.power_factor }}</strong></div>
          </div>
        </section>

        <section class="card detail-section">
          <h3><Activity :size="22" color="#059669" /> {{ ui.t('electricalParameters') }}</h3>
          <div class="parameter-grid">
            <div class="parameter"><span>{{ ui.t('voltage') }}</span><strong>{{ liveDevice.vrms }} V</strong></div>
            <div class="parameter" style="border-color:#ef4444"><span>{{ ui.t('current') }}</span><strong>{{ liveDevice.irms }} A</strong></div>
            <div class="parameter" style="border-color:#a855f7"><span>{{ ui.t('phase') }}</span><strong>{{ liveDevice.phase }}°</strong></div>
            <div class="parameter" style="border-color:#f59e0b"><span>{{ ui.t('frequency') }}</span><strong>{{ liveDevice.frequency }} Hz</strong></div>
          </div>
        </section>

        <section class="card detail-section">
          <h3><Activity :size="22" color="#059669" /> {{ ui.t('additionalInfo') }}</h3>
          <div class="info-grid">
            <div class="info-row"><span>{{ ui.t('deviceStatus') }}</span><StatusBadge :status="liveDevice.status" /></div>
            <div class="info-row"><span>{{ ui.t('lastUpdate') }}</span><strong>{{ formatTime(liveDevice.timestamp) }}</strong></div>
            <div class="info-row"><span>{{ ui.t('estimatedDaily') }}</span><strong>{{ liveDevice.energy_kwh }} kWh</strong></div>
            <div class="info-row"><span>{{ ui.t('frontendConnection') }}</span><strong>HTTP API REST</strong></div>
          </div>
        </section>
      </aside>
    </Transition>
  </Teleport>
</template>

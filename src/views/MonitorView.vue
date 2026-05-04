<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useDeviceStore } from '../stores/devices'
import { useUiStore } from '../stores/ui'
import DeviceCard from '../components/devices/DeviceCard.vue'
import DeviceDetailDrawer from '../components/devices/DeviceDetailDrawer.vue'
import PowerlytixLogo from '../components/ui/PowerlytixLogo.vue'

const devices = useDeviceStore()
const ui = useUiStore()
const selected = ref(null)
let timer

function updateSelected(device) {
  if (selected.value && device.device_id === selected.value.device_id) selected.value = device
}

onMounted(async () => {
  await devices.fetchDevices()
  timer = setInterval(devices.fetchDevices, 5000)
})
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <section>
    <div class="page-header">
      <div>
        <h1>{{ ui.t('monitorTitle') }}</h1>
        <p>{{ ui.t('monitorSubtitle') }}</p>
      </div>
    </div>
    <div class="card hero-card">
      <div>
        <span>{{ ui.t('currentTotal') }}</span>
        <div class="hero-value">{{ Math.round(devices.totalPower) }} <small>W</small></div>
        <span>{{ devices.activeCount }} {{ ui.t('of') }} {{ devices.devices.length }} {{ ui.t('activeDevices') }}</span>
      </div>
      <div class="hero-icon"><PowerlytixLogo mark-only /></div>
    </div>
    <h2 style="margin-top:24px">{{ ui.t('devices') }}</h2>
    <div class="grid device-grid">
      <DeviceCard v-for="device in devices.devices" :key="device.device_id" :device="device" @select="selected = $event" />
    </div>
    <DeviceDetailDrawer :device="selected" @close="selected = null" @updated="updateSelected" />
  </section>
</template>

<script setup>
import { computed } from 'vue'
import DeviceIcon from '../devices/DeviceIcon.vue'

const props = defineProps({
  devices: { type: Array, default: () => [] },
  metric: { type: String, default: 'active_power' },
  unit: { type: String, default: 'W' },
})
const max = computed(() => Math.max(...props.devices.map((device) => metricValue(device)), 1))
const palette = ['#0f766e', '#2563eb', '#7c3aed', '#dc2626', '#ea580c', '#0891b2', '#65a30d', '#9333ea']

function metricValue(device) {
  return Number(device?.[props.metric] ?? device?.active_power ?? 0)
}

function formatValue(value) {
  return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: props.unit === 'W' || props.unit === 'VAR' || props.unit === 'VA' ? 0 : 2 })
}

function barStyle(device, index) {
  const color = device.color || palette[index % palette.length]
  const width = Math.max(8, (metricValue(device) / max.value) * 100)
  return {
    width: `${width}%`,
    background: `linear-gradient(90deg, ${color}, ${color}cc)`,
  }
}
</script>

<template>
  <div class="clean-bars">
    <div v-for="(device, index) in devices" :key="device.device_id" class="bar-row">
      <div>
        <strong class="bar-device-name"><span class="mini-device-icon"><DeviceIcon :icon="device.icon" :size="16" /></span>{{ device.name }}</strong>
        <span>{{ formatValue(metricValue(device)) }} {{ unit }}</span>
      </div>
      <div class="bar-track">
        <span :style="barStyle(device, index)"></span>
      </div>
    </div>
  </div>
</template>

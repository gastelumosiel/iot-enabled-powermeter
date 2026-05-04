<script setup>
import { computed } from 'vue'

const props = defineProps({ devices: { type: Array, default: () => [] } })
const max = computed(() => Math.max(...props.devices.map((device) => Number(device.active_power || 0)), 1))
const palette = ['#047857', '#10b981', '#34d399', '#0f766e', '#65a30d']

function barStyle(device, index) {
  const color = palette[index % palette.length]
  const width = Math.max(8, (Number(device.active_power || 0) / max.value) * 100)
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
        <strong>{{ device.name }}</strong>
        <span>{{ Math.round(device.active_power) }} W</span>
      </div>
      <div class="bar-track">
        <span :style="barStyle(device, index)"></span>
      </div>
    </div>
  </div>
</template>

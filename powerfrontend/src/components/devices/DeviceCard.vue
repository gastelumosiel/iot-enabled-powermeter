<script setup>
import { Menu } from 'lucide-vue-next'
import { useUiStore } from '../../stores/ui'
import DeviceIcon from './DeviceIcon.vue'
import { formatAppTime } from '../../utils/datetime'

defineProps({ device: { type: Object, required: true } })
defineEmits(['select'])
const ui = useUiStore()

function formatTime(value) {
  return formatAppTime(value, ui.language === 'ES' ? 'es-MX' : 'en-US') || ui.t('noData')
}
</script>

<template>
  <article class="device-card">
    <div class="device-head">
      <span class="icon-box" style="background:#d1fae5;color:#059669"><DeviceIcon :icon="device.icon" :size="21" /></span>
      <div>
        <h3>{{ device.name }}</h3>
        <small class="muted">{{ ui.t('deviceId') }}: {{ device.device_id }}</small>
      </div>
      <span class="status-dot" :class="device.status"></span>
      <button class="more-btn" type="button" :aria-label="ui.t('moreOptions')" @click="$emit('select', device)">
        <Menu :size="19" />
      </button>
    </div>
    <div class="power-row">
      <strong>{{ Math.round(device.active_power) }}</strong>
      <span>W</span>
    </div>
    <div class="updated">{{ ui.t('lastUpdate') }}: {{ formatTime(device.timestamp) }}</div>
  </article>
</template>

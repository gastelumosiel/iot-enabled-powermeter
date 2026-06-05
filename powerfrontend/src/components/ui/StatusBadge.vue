<script setup>
import { useUiStore } from '../../stores/ui'

defineProps({ status: { type: String, default: 'offline' } })
const ui = useUiStore()

function statusLabel(status) {
  return ui.t(['online', 'idle', 'offline'].includes(status) ? status : 'offline')
}
</script>

<template>
  <span class="pill" :class="status">
    <span class="status-dot" :class="status"></span>
    {{ statusLabel(status) }}
  </span>
</template>

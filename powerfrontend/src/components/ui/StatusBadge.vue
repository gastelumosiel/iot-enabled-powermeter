<script setup>
import { useUiStore } from '../../stores/ui'

defineProps({ status: { type: String, default: 'offline' } })
const ui = useUiStore()
</script>

<template>
  <span class="pill" :class="status">
    <span class="status-dot" :class="status"></span>
    {{ status === 'online' ? ui.t('online') : ui.t('offline') }}
  </span>
</template>

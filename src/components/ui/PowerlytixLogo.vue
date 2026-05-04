<script setup>
import { useUiStore } from '../../stores/ui'

defineProps({
  compact: { type: Boolean, default: false },
  markOnly: { type: Boolean, default: false },
})

const ui = useUiStore()
</script>

<template>
  <div class="logo-lockup" :class="{ compact }">
    <span class="power-logo-icon" aria-hidden="true">
      <svg viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="48" fill="none" stroke="#2dd4a3" stroke-width="8" />
        <path d="M65 22 34 64h25l-6 34 34-47H63l2-29Z" fill="none" stroke="#fde047" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </span>
    <div v-if="!compact && !markOnly" class="logo-text">
      <strong><span>POWER</span><em>LYTIX</em></strong>
      <span>{{ ui.t('logoTagline') }}</span>
    </div>
  </div>
</template>

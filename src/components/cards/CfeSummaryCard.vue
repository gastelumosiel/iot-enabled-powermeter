<script setup>
import { useUiStore } from '../../stores/ui'

defineProps({ summary: { type: Object, required: true } })
const ui = useUiStore()
</script>

<template>
  <section class="stat-card stat-green">
    <span>{{ ui.t('cfeRate') }}</span>
    <strong>{{ summary.accumulated_kwh?.toFixed?.(2) || summary.accumulated_kwh }} kWh</strong>
    <div class="cfe-progress"><span :style="{ width: `${Math.min(summary.usage_percent || 0, 100)}%` }"></span></div>
    <small>
      {{ ui.t('configuredLimit') }} {{ summary.configured_limit }} kWh · {{ Math.round(summary.usage_percent || 0) }}% {{ ui.t('used') }} ·
      {{ summary.remaining_kwh?.toFixed?.(1) || summary.remaining_kwh }} kWh {{ ui.t('remaining') }}
    </small>
  </section>
</template>

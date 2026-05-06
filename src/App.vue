<script setup>
import { onMounted, ref, watch } from 'vue'
import { useUiStore } from './stores/ui'

const ui = useUiStore()
const uiShift = ref(false)
let uiTimer

onMounted(() => ui.hydrate())

watch(() => [ui.language, ui.theme], () => {
  uiShift.value = false
  window.clearTimeout(uiTimer)
  requestAnimationFrame(() => {
    uiShift.value = true
    uiTimer = window.setTimeout(() => { uiShift.value = false }, 240)
  })
})
</script>

<template>
  <div :class="{ 'ui-shift': uiShift }">
    <RouterView v-slot="{ Component, route }">
      <Transition name="route-fade" mode="out-in">
        <component :is="Component" :key="route.meta.public ? route.fullPath : 'app-shell'" />
      </Transition>
    </RouterView>
  </div>
</template>

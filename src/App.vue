<script setup>
import { onMounted } from 'vue'
import { useUiStore } from './stores/ui'

const ui = useUiStore()

onMounted(() => ui.hydrate())
</script>

<template>
  <RouterView v-slot="{ Component, route }">
    <Transition name="route-fade" mode="out-in">
      <component :is="Component" :key="route.meta.public ? route.fullPath : 'app-shell'" />
    </Transition>
  </RouterView>
</template>

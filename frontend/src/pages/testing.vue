
<script setup lang="ts">
import { ref, shallowRef } from 'vue'
import { sub } from 'date-fns'
import type { Period, Range } from '../types'

const range = shallowRef<Range>({
  start: sub(new Date(), { days: 14 }),
  end: new Date()
})
const period = ref<Period>('daily')
</script>

<template>
  <UDashboardPanel id="testing">
    <template #header>
      <UDashboardNavbar title="testing">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <CustomersAddModal />
        </template>
      </UDashboardNavbar>

    </template>

    <template #body>
      <DataChart :period="period" :range="range" />
    </template>
  </UDashboardPanel>
</template>
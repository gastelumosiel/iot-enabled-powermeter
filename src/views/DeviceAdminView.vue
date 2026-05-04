<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { Info, Plus, Trash2 } from 'lucide-vue-next'
import { useDeviceStore } from '../stores/devices'
import { useUiStore } from '../stores/ui'
import StatusBadge from '../components/ui/StatusBadge.vue'
import DeviceIcon from '../components/devices/DeviceIcon.vue'

const devices = useDeviceStore()
const ui = useUiStore()
const showForm = ref(false)
const form = ref({ device_id: '', name: '', icon: 'plug' })
const isMutating = ref(false)
const cooldownUntil = ref(0)
const pendingDelete = ref(null)
let timer

const iconOptions = [
  { value: 'air', label: 'iconAir' },
  { value: 'computer', label: 'iconComputer' },
  { value: 'fridge', label: 'iconFridge' },
  { value: 'washer', label: 'iconWasher' },
  { value: 'microwave', label: 'iconMicrowave' },
  { value: 'lamp', label: 'iconLamp' },
  { value: 'tv', label: 'iconTv' },
  { value: 'fan', label: 'iconFan' },
  { value: 'heater', label: 'iconHeater' },
  { value: 'router', label: 'iconRouter' },
  { value: 'printer', label: 'iconPrinter' },
  { value: 'phone', label: 'iconPhone' },
  { value: 'tablet', label: 'iconTablet' },
  { value: 'speaker', label: 'iconSpeaker' },
  { value: 'console', label: 'iconConsole' },
  { value: 'coffee', label: 'iconCoffee' },
  { value: 'kitchen', label: 'iconKitchen' },
  { value: 'bulb', label: 'iconBulb' },
  { value: 'battery', label: 'iconBattery' },
  { value: 'cable', label: 'iconCable' },
  { value: 'outlet', label: 'iconOutlet' },
  { value: 'plug', label: 'iconPlug' },
]

function formatTime(value) {
  return value ? new Date(value).toLocaleTimeString(ui.language === 'ES' ? 'es-MX' : 'en-US') : ui.t('noData')
}

async function addDevice() {
  if (!form.value.device_id || !form.value.name || isMutating.value) return
  isMutating.value = true
  cooldownUntil.value = Date.now() + 2200
  try {
    await devices.addDevice({ ...form.value })
    form.value = { device_id: '', name: '', icon: 'plug' }
    showForm.value = false
  } finally {
    window.setTimeout(() => { isMutating.value = false }, 700)
  }
}

async function removeDevice(id) {
  if (isMutating.value) return
  isMutating.value = true
  cooldownUntil.value = Date.now() + 2200
  try {
    await devices.deleteDevice(id)
  } finally {
    window.setTimeout(() => { isMutating.value = false }, 700)
  }
}

function askDelete(device) {
  pendingDelete.value = device
}

async function confirmDelete() {
  if (!pendingDelete.value) return
  const id = pendingDelete.value.device_id
  pendingDelete.value = null
  await removeDevice(id)
}

async function refreshDevices() {
  if (Date.now() < cooldownUntil.value || isMutating.value) return
  await devices.fetchDevices()
}

onMounted(async () => {
  await devices.fetchDevices()
  timer = setInterval(refreshDevices, 7000)
})
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <section>
    <div class="page-header">
      <div><h1>{{ ui.t('manageTitle') }}</h1><p>{{ ui.t('manageSubtitle') }}</p></div>
      <button class="btn btn-primary" @click="showForm = !showForm"><Plus :size="19" /> {{ ui.t('addDevice') }}</button>
    </div>

    <Transition name="slide-fade">
      <form v-if="showForm" class="card admin-form" @submit.prevent="addDevice">
        <h2>{{ ui.t('newDevice') }}</h2>
        <div class="field"><label>{{ ui.t('deviceIdLabel') }}</label><input v-model="form.device_id" class="input" :placeholder="ui.t('deviceIdPlaceholder')" /></div>
        <div class="field"><label>{{ ui.t('deviceNameLabel') }}</label><input v-model="form.name" class="input" :placeholder="ui.t('deviceNamePlaceholder')" /></div>
        <div class="field">
          <label>{{ ui.t('iconLabel') }}</label>
          <div class="icon-picker">
            <button
              v-for="option in iconOptions"
              :key="option.value"
              type="button"
              class="icon-choice"
              :class="{ selected: form.icon === option.value }"
              @click="form.icon = option.value"
            >
              <DeviceIcon :icon="option.value" :size="20" />
              <span>{{ ui.t(option.label) }}</span>
            </button>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn btn-primary" :disabled="isMutating">{{ ui.t('addDeviceAction') }}</button>
          <button type="button" class="btn btn-secondary" :disabled="isMutating" @click="showForm=false">{{ ui.t('cancel') }}</button>
        </div>
      </form>
    </Transition>

    <div class="card table-card">
      <table>
        <thead><tr><th>{{ ui.t('device') }}</th><th>{{ ui.t('deviceId') }}</th><th>{{ ui.t('status') }}</th><th>{{ ui.t('power') }}</th><th>{{ ui.t('actions') }}</th></tr></thead>
        <tbody>
          <tr v-for="device in devices.devices" :key="device.device_id">
            <td><div class="device-cell"><span class="icon-box" style="background:#d1fae5;color:#059669"><DeviceIcon :icon="device.icon" /></span><div><strong>{{ device.name }}</strong><br><span class="muted">{{ ui.t('updated') }} {{ formatTime(device.timestamp) }}</span></div></div></td>
            <td>{{ device.device_id }}</td>
            <td><StatusBadge :status="device.status" /></td>
            <td><strong>{{ Math.round(device.active_power) }} W</strong></td>
            <td><button class="btn btn-danger" :disabled="isMutating" :title="ui.t('delete')" @click="askDelete(device)"><Trash2 :size="18" /></button></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="info-box">
      <h3><Info :size="20" /> {{ ui.t('importantInfo') }}</h3>
      <p>- {{ ui.t('uniqueIdInfo') }}</p>
      <p>- {{ ui.t('offlineInfo') }}</p>
      <p>- {{ ui.t('cooldownInfo') }}</p>
    </div>
    <Transition name="modal-fade">
      <div v-if="pendingDelete" class="modal-overlay" @click="pendingDelete = null">
        <section class="confirm-modal" @click.stop>
          <div class="confirm-icon"><Trash2 :size="24" /></div>
          <h2>{{ ui.t('confirmDeleteTitle') }}</h2>
          <p>{{ ui.t('confirmDeleteCopy') }}</p>
          <strong>{{ pendingDelete.name }}</strong>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="pendingDelete = null">{{ ui.t('keepDevice') }}</button>
            <button type="button" class="btn btn-primary" @click="confirmDelete">{{ ui.t('delete') }}</button>
          </div>
        </section>
      </div>
    </Transition>
  </section>
</template>

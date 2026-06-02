<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { LogOut } from 'lucide-vue-next'
import { userService } from '../services/userService'
import { cfeService } from '../services/cfeService'
import { useAuthStore } from '../stores/auth'
import { useUiStore } from '../stores/ui'

const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()
const profile = ref({
  name: auth.user?.name || 'Usuario PowerLytix',
  email: auth.user?.email || 'usuario@powerlytix.com',
  devices_count: 0,
  cfe_rate: 'Domestica 1C',
  bimonthly_limit_kwh: 280,
  created_at: new Date().toISOString(),
})

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString(ui.language === 'ES' ? 'es-MX' : 'en-US') : ui.t('noData')
}

function logout() {
  auth.logout()
  router.push('/login')
}

function applyLocalCfeProfile() {
  const savedRate = localStorage.getItem('powerlytix_cfe_rate') || 'domestic_1c'
  const tariff = cfeService.localTariff(savedRate)
  profile.value = {
    ...profile.value,
    cfe_rate: tariff.label,
    bimonthly_limit_kwh: Number(tariff.monthlyLimit || 0) * 2,
  }
}

onMounted(async () => {
  profile.value = { ...profile.value, ...(await userService.profile()) }
  applyLocalCfeProfile()
  window.addEventListener('powerlytix:cfe-settings-saved', applyLocalCfeProfile)
})

onUnmounted(() => {
  window.removeEventListener('powerlytix:cfe-settings-saved', applyLocalCfeProfile)
})
</script>

<template>
  <section>
    <div class="page-header">
      <div><h1>{{ ui.t('profileTitle') }}</h1><p>{{ ui.t('profileSubtitle') }}</p></div>
      <button class="btn btn-primary" @click="logout"><LogOut :size="18" /> {{ ui.t('logout') }}</button>
    </div>

    <div class="profile-panel card">
      <div class="profile-banner">
        <h2>{{ ui.t('yourProfile') }}</h2>
        <div class="profile-avatar">{{ profile.name.slice(0, 1).toUpperCase() }}</div>
      </div>
      <div class="profile-content">
        <dl class="profile-list">
          <div><dt>{{ ui.t('name') }}</dt><dd>{{ profile.name }}</dd></div>
          <div><dt>{{ ui.t('email') }}</dt><dd>{{ profile.email }}</dd></div>
          <div><dt>{{ ui.t('deviceCount') }}</dt><dd>{{ profile.devices_count }}</dd></div>
          <div><dt>{{ ui.t('configuredCfeRate') }}</dt><dd>{{ profile.cfe_rate }}</dd></div>
          <div><dt>{{ ui.t('bimonthlyLimit') }}</dt><dd>{{ profile.bimonthly_limit_kwh }} kWh</dd></div>
          <div><dt>{{ ui.t('createdAt') }}</dt><dd>{{ formatDate(profile.created_at) }}</dd></div>
        </dl>
        <button class="btn btn-primary" disabled>{{ ui.t('edit') }}</button>
      </div>
    </div>
  </section>
</template>

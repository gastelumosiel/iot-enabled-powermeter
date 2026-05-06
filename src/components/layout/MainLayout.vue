<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Check, Languages, LayoutDashboard, LineChart, ReceiptText, Settings, User, LogOut, Moon, Sun, Zap } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useDeviceStore } from '../../stores/devices'
import { useUiStore } from '../../stores/ui'
import PowerlytixLogo from '../ui/PowerlytixLogo.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const devices = useDeviceStore()
const ui = useUiStore()
const languageOpen = ref(false)
const userOpen = ref(false)
const languageRef = ref(null)
const userRef = ref(null)

function closePopups() {
  languageOpen.value = false
  userOpen.value = false
}

function onDocumentPointerDown(event) {
  if (!languageRef.value?.contains(event.target)) languageOpen.value = false
  if (!userRef.value?.contains(event.target)) userOpen.value = false
}

onMounted(() => {
  ui.hydrate()
  document.addEventListener('pointerdown', onDocumentPointerDown)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', onDocumentPointerDown)
})

watch(() => route.fullPath, closePopups)

function logout() {
  auth.logout()
  router.push('/login')
}

function setLanguage(language) {
  ui.setLanguage(language)
  languageOpen.value = false
}
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="side-brand">
        <PowerlytixLogo />
      </div>
      <nav class="nav">
        <RouterLink class="nav-link" to="/monitor"><LayoutDashboard :size="19" /><span>{{ ui.t('monitor') }}</span></RouterLink>
        <RouterLink class="nav-link" to="/analytics"><LineChart :size="19" /><span>{{ ui.t('analytics') }}</span></RouterLink>
        <RouterLink class="nav-link" to="/cfe"><ReceiptText :size="19" /><span>{{ ui.t('cfe') }}</span></RouterLink>
        <RouterLink class="nav-link" to="/admin/devices"><Settings :size="19" /><span>{{ ui.t('admin') }}</span></RouterLink>
      </nav>
      <div class="side-bottom">
        <div class="side-total">
          <span><Zap :size="16" color="#fde047" /> {{ ui.t('total') }}</span>
          <strong>{{ Math.round(devices.totalPower) }} W</strong>
          <small>{{ devices.activeCount }} {{ ui.t('activeDevices') }}</small>
        </div>
        <div class="sidebar-controls">
          <div ref="languageRef" class="language-picker">
            <button class="sidebar-control" type="button" @click="languageOpen = !languageOpen">
              <Languages :size="16" />
              <span>{{ ui.language }}</span>
            </button>
            <Transition name="popup-fade">
              <div v-if="languageOpen" class="language-menu">
                <button type="button" @click="setLanguage('ES')"><span>{{ ui.t('languageSpanish') }}</span><Check v-if="ui.language === 'ES'" :size="15" /></button>
                <button type="button" @click="setLanguage('EN')"><span>{{ ui.t('languageEnglish') }}</span><Check v-if="ui.language === 'EN'" :size="15" /></button>
              </div>
            </Transition>
          </div>
          <button class="theme-toggle icon-only" type="button" :aria-label="ui.theme === 'light' ? ui.t('light') : ui.t('dark')" @click="ui.toggleTheme">
            <Sun v-if="ui.theme === 'light'" :size="16" />
            <Moon v-else :size="16" />
          </button>
        </div>
        <div ref="userRef" class="user-menu-wrap">
          <button class="user-chip" type="button" @click="userOpen = !userOpen">
            <span class="user-avatar">{{ (auth.user?.name || auth.user?.email || 'U').slice(0, 1).toUpperCase() }}</span>
            <span class="user-meta">
              <strong>{{ auth.user?.name || 'PowerLytix' }}</strong>
              <small>{{ ui.t('account') }}</small>
            </span>
          </button>
          <Transition name="popup-fade">
            <div v-if="userOpen" class="user-popup">
              <div class="user-popup-head">
                <span class="user-avatar large">{{ (auth.user?.name || auth.user?.email || 'U').slice(0, 1).toUpperCase() }}</span>
                <div>
                  <strong>{{ auth.user?.name || 'PowerLytix' }}</strong>
                  <small>{{ auth.user?.email || 'usuario@powerlytix.com' }}</small>
                </div>
              </div>
              <RouterLink class="popup-action" to="/profile" @click="userOpen = false"><User :size="17" />{{ ui.t('viewProfile') }}</RouterLink>
              <button class="popup-action danger" type="button" @click="logout"><LogOut :size="17" />{{ ui.t('logout') }}</button>
            </div>
          </Transition>
        </div>
      </div>
    </aside>
    <main class="main">
      <RouterView v-slot="{ Component, route }">
        <Transition name="route-fade" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </Transition>
      </RouterView>
    </main>
  </div>
</template>

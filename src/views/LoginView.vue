<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Check, Languages, LineChart, Moon, Sun, Zap } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { useUiStore } from '../stores/ui'
import PowerlytixLogo from '../components/ui/PowerlytixLogo.vue'

const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()
const email = ref('')
const password = ref('')
const error = ref('')
const languageOpen = ref(false)
const languageRef = ref(null)

function setLanguage(language) {
  ui.setLanguage(language)
  languageOpen.value = false
}

function onDocumentPointerDown(event) {
  if (!languageRef.value?.contains(event.target)) languageOpen.value = false
}

onMounted(() => document.addEventListener('pointerdown', onDocumentPointerDown))
onBeforeUnmount(() => document.removeEventListener('pointerdown', onDocumentPointerDown))

async function submit() {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = ui.t('missingLogin')
    return
  }
  await auth.login({ email: email.value, password: password.value })
  router.push('/monitor')
}
</script>

<template>
  <div class="auth-shell">
    <section class="auth-brand">
      <div class="auth-controls">
        <div ref="languageRef" class="language-picker auth-language">
          <button type="button" @click="languageOpen = !languageOpen"><Languages :size="15" /> {{ ui.language }}</button>
          <Transition name="popup-fade">
            <div v-if="languageOpen" class="language-menu">
              <button type="button" @click="setLanguage('ES')"><span>{{ ui.t('languageSpanish') }}</span><Check v-if="ui.language === 'ES'" :size="15" /></button>
              <button type="button" @click="setLanguage('EN')"><span>{{ ui.t('languageEnglish') }}</span><Check v-if="ui.language === 'EN'" :size="15" /></button>
            </div>
          </Transition>
        </div>
        <button type="button" class="theme-icon-btn" :aria-label="ui.theme === 'light' ? ui.t('light') : ui.t('dark')" @click="ui.toggleTheme">
          <Sun v-if="ui.theme === 'light'" :size="15" />
          <Moon v-else :size="15" />
        </button>
      </div>
      <div class="brand-panel"><PowerlytixLogo /></div>
      <div class="auth-copy">
        <h1>{{ ui.t('loginHeroTitle') }}</h1>
        <p>{{ ui.t('loginHeroCopy') }}</p>
        <div class="auth-feature"><span class="icon-box"><Zap /></span><div><strong>{{ ui.t('realtimeMonitoring') }}</strong><span>{{ ui.t('realtimeMonitoringCopy') }}</span></div></div>
        <div class="auth-feature"><span class="icon-box"><LineChart /></span><div><strong>{{ ui.t('advancedAnalytics') }}</strong><span>{{ ui.t('advancedAnalyticsCopy') }}</span></div></div>
      </div>
      <small>{{ ui.t('loginFooter') }}</small>
    </section>
    <section class="auth-form-wrap">
      <form class="auth-card" @submit.prevent="submit">
        <h2>{{ ui.t('welcomeBack') }}</h2>
        <p>{{ ui.t('credentialsCopy') }}</p>
        <div class="field"><label>{{ ui.t('emailLabel') }}</label><input v-model="email" class="input" type="email" placeholder="tu@email.com" /></div>
        <div class="field"><label>{{ ui.t('passwordLabel') }}</label><input v-model="password" class="input" type="password" placeholder="********" /></div>
        <div v-if="error" class="error-text">{{ error }}</div>
        <button class="btn btn-primary btn-full">{{ ui.t('signIn') }}</button>
        <RouterLink class="auth-link" to="/register">{{ ui.t('noAccount') }}</RouterLink>
      </form>
    </section>
  </div>
</template>

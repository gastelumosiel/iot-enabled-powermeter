<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Check, Languages, Moon, Sun, Zap } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { useUiStore } from '../stores/ui'
import PowerlytixLogo from '../components/ui/PowerlytixLogo.vue'

const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()
const form = ref({ name: '', email: '', password: '', confirm: '' })
const error = ref('')
const loading = ref(false)
const languageOpen = ref(false)
const languageRef = ref(null)

function setLanguage(language) {
  ui.setLanguage(language)
  languageOpen.value = false
}

function onDocumentPointerDown(event) {
  if (!languageRef.value?.contains(event.target)) languageOpen.value = false
}

function requestErrorMessage(err) {
  return err?.response?.data?.detail
    || err?.response?.data?.error
    || err?.message
    || 'No se pudo crear la cuenta.'
}

onMounted(() => document.addEventListener('pointerdown', onDocumentPointerDown))
onBeforeUnmount(() => document.removeEventListener('pointerdown', onDocumentPointerDown))

async function submit() {
  error.value = ''
  if (loading.value) return
  if (!form.value.name || !form.value.email || !form.value.password) error.value = ui.t('completeFields')
  else if (form.value.password !== form.value.confirm) error.value = ui.t('passwordsMismatch')
  if (error.value) return
  loading.value = true
  try {
    await auth.register(form.value)
    router.push('/monitor')
  } catch (err) {
    error.value = requestErrorMessage(err)
  } finally {
    loading.value = false
  }
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
        <h1>{{ ui.t('registerHeroTitle') }}</h1>
        <p>{{ ui.t('registerHeroCopy') }}</p>
        <div class="auth-feature"><span class="icon-box"><Zap /></span><div><strong>{{ ui.t('iotPlugin') }}</strong><span>{{ ui.t('apiReady') }}</span></div></div>
      </div>
      <small>{{ ui.t('registerFooter') }}</small>
    </section>
    <section class="auth-form-wrap">
      <form class="auth-card" @submit.prevent="submit">
        <h2>{{ ui.t('createAccount') }}</h2>
        <p>{{ ui.t('configureAccess') }}</p>
        <div class="field"><label>{{ ui.t('name') }}</label><input v-model="form.name" class="input" :placeholder="ui.t('namePlaceholder')" /></div>
        <div class="field"><label>{{ ui.t('emailLabel') }}</label><input v-model="form.email" class="input" type="email" placeholder="tu@email.com" /></div>
        <div class="field"><label>{{ ui.t('passwordLabel') }}</label><input v-model="form.password" class="input" type="password" /></div>
        <div class="field"><label>{{ ui.t('confirmation') }}</label><input v-model="form.confirm" class="input" type="password" /></div>
        <div v-if="error" class="error-text">{{ error }}</div>
        <button class="btn btn-primary btn-full" :disabled="loading">{{ ui.t('register') }}</button>
        <RouterLink class="auth-link" to="/login">{{ ui.t('hasAccount') }}</RouterLink>
      </form>
    </section>
  </div>
</template>

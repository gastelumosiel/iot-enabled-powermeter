import { defineStore } from 'pinia'
import { authService } from '../services/authService'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('powerlytix_token') || '',
    user: JSON.parse(localStorage.getItem('powerlytix_user') || 'null'),
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },
  actions: {
    async login(credentials) {
      const { data } = await authService.login(credentials)
      this.token = data.token || data.access || data.key
      if (!this.token) throw new Error('Authentication token missing from response.')
      this.user = data.user || { email: credentials.email, name: 'Usuario PowerLytix' }
      
      localStorage.setItem('powerlytix_token', this.token)
      localStorage.setItem('powerlytix_user', JSON.stringify(this.user))
    },
    async register(payload) {
      const { data } = await authService.register(payload)
      this.token = data.token || data.access || data.key
      if (!this.token) throw new Error('Authentication token missing from response.')
      this.user = data.user || { email: payload.email, name: payload.name }
      localStorage.setItem('powerlytix_token', this.token)
      localStorage.setItem('powerlytix_user', JSON.stringify(this.user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('powerlytix_token')
      localStorage.removeItem('powerlytix_user')
    },
  },
})

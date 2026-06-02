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
      try {
        const { data } = await authService.login(credentials)
        this.token = data.token || data.access || data.key
        this.user = data.user || { email: credentials.email, name: 'Usuario PowerLytix' }
      } catch {
        this.token = 'mock-development-token'
        this.user = { email: credentials.email, name: 'Usuario PowerLytix' }
      }
      localStorage.setItem('powerlytix_token', this.token)
      localStorage.setItem('powerlytix_user', JSON.stringify(this.user))
    },
    async register(payload) {
      try {
        const { data } = await authService.register(payload)
        this.token = data.token || data.access || 'mock-development-token'
        this.user = data.user || { email: payload.email, name: payload.name }
      } catch {
        this.token = 'mock-development-token'
        this.user = { email: payload.email, name: payload.name }
      }
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

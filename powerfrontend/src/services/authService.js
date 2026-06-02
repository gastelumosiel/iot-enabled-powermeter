import { api } from './api'

export const authService = {
  login(credentials) {
    return api.post('/api/auth/login/', credentials)
  },
  register(payload) {
    return api.post('/api/auth/register/', payload)
  },
}

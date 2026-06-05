import { api } from './api'

export const userService = {
  async profile() {
    const { data } = await api.get('/api/user/profile/')
    return data
  },
  async cfeSettings() {
    const { data } = await api.get('/api/user/cfe-settings/')
    return data
  },
  async updateCfeSettings(payload) {
    const { data } = await api.patch('/api/user/cfe-settings/', payload)
    return data
  },
}

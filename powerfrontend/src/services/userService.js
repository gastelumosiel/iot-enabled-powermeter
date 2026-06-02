import { api } from './api'
import { mockProfile } from '../mocks/devices'

export const userService = {
  async profile() {
    if (!navigator.onLine) return mockProfile
    try {
      const response = await api.get('/api/user/profile/')
      return response.data
    } catch {
      return mockProfile
    }
  },
}

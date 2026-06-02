import { api } from './api'
import { makePowerHistory, mockCfeSummary } from '../mocks/devices'

async function fallback(callback, waitMs = 450) {
  try {
    return await Promise.race([
      callback(),
      new Promise((resolve) => setTimeout(() => resolve(null), waitMs)),
    ])
  } catch {
    return null
  }
}

export const analyticsService = {
  async history(params) {
    const response = await fallback(() => api.get('/api/analytics/history/', { params }))
    return response?.data || makePowerHistory(params?.range)
  },
  async cfeSummary() {
    const response = await fallback(() => api.get('/api/cfe/summary/'))
    return response?.data || mockCfeSummary
  },
}

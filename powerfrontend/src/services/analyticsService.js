import { api } from './api'

export const analyticsService = {
  async history(params) {
    const response = await api.get('/api/analytics/history/', { params })
    return response.data
  },
  async availability(params) {
    const response = await api.get('/api/analytics/availability/', { params })
    return response.data
  },
  async cfeSummary(params) {
    const response = await api.get('/api/cfe/summary/', { params })
    return response.data
  },
}

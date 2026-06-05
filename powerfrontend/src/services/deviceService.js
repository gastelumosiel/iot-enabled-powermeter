import { api } from './api'

export const deviceService = {
  async list() {
    const { data } = await api.get('/api/devices/')
    return data
  },
  async getById(id) {
    const { data } = await api.get(`/api/devices/${id}/`)
    return data
  },
  async create(payload) {
    const { data } = await api.post('/api/devices/', payload)
    return data
  },
  async update(id, payload) {
    const { data } = await api.patch(`/api/devices/${id}/`, payload)
    return data
  },
  async remove(id) {
    await api.delete(`/api/devices/${id}/`)
    return { ok: true }
  },
}

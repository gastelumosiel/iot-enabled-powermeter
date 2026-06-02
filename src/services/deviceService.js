import { api } from './api'
import { mockDevices, withLiveNoise } from '../mocks/devices'

let localDevices = [...mockDevices]

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

export const deviceService = {
  async list() {
    const response = await fallback(() => api.get('/api/devices/'))
    if (response?.data) return response.data
    localDevices = withLiveNoise(localDevices)
    return localDevices
  },
  async getById(id) {
    const response = await fallback(() => api.get(`/api/devices/${id}/`))
    if (response?.data) return response.data
    localDevices = withLiveNoise(localDevices)
    return localDevices.find((device) => device.device_id === id || device.id === id)
  },
  async create(payload) {
    const response = await fallback(() => api.post('/api/devices/', payload))
    if (response?.data) return response.data
    const device = {
      id: payload.device_id,
      device_id: payload.device_id,
      name: payload.name,
      icon: payload.icon || 'plug',
      timestamp: new Date().toISOString(),
      vrms: 0,
      irms: 0,
      active_power: 0,
      reactive_power: 0,
      apparent_power: 0,
      power_factor: 0,
      phase: 0,
      frequency: 0,
      energy_kwh: 0,
      status: 'offline',
    }
    localDevices = [device, ...localDevices]
    return device
  },
  async update(id, payload) {
    const response = await fallback(() => api.patch(`/api/devices/${id}/`, payload))
    if (response?.data) return response.data
    localDevices = localDevices.map((device) => (
      device.device_id === id || device.id === id ? { ...device, ...payload, timestamp: new Date().toISOString() } : device
    ))
    return localDevices.find((device) => device.device_id === id || device.id === id)
  },
  async remove(id) {
    const response = await fallback(() => api.delete(`/api/devices/${id}/`))
    localDevices = localDevices.filter((device) => device.device_id !== id && device.id !== id)
    return response?.data || { ok: true }
  },
}

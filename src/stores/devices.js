import { defineStore } from 'pinia'
import { deviceService } from '../services/deviceService'

export const useDeviceStore = defineStore('devices', {
  state: () => ({
    devices: [],
    loading: false,
  }),
  getters: {
    totalPower: (state) => state.devices.reduce((sum, device) => sum + Number(device.active_power || 0), 0),
    activeCount: (state) => state.devices.filter((device) => device.status === 'online').length,
  },
  actions: {
    async fetchDevices() {
      this.loading = true
      this.devices = await deviceService.list()
      this.loading = false
    },
    async fetchDevice(id) {
      const device = await deviceService.getById(id)
      const index = this.devices.findIndex((item) => item.device_id === id || item.id === id)
      if (index >= 0 && device) this.devices[index] = device
      return device
    },
    async addDevice(payload) {
      const device = await deviceService.create(payload)
      await this.fetchDevices()
      return device
    },
    async updateDevice(id, payload) {
      const device = await deviceService.update(id, payload)
      const index = this.devices.findIndex((item) => item.device_id === id || item.id === id)
      if (index >= 0 && device) this.devices[index] = device
      return device
    },
    async deleteDevice(id) {
      await deviceService.remove(id)
      this.devices = this.devices.filter((device) => device.device_id !== id && device.id !== id)
    },
  },
})

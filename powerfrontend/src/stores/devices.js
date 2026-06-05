import { defineStore } from 'pinia'
import { deviceService } from '../services/deviceService'
import { applyEmaFilter } from '../utils/emaFilter'

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
    smoothDevice(device) {
      // return device
      const previous = this.devices.find((item) => item.device_id === device.device_id || item.id === device.id)
      return applyEmaFilter(previous, device)
    },
    async fetchDevices() {
      this.loading = true
      const data = await deviceService.list()
      this.devices = data.map((device) => this.smoothDevice(device))
      this.loading = false
    },
    async fetchDevice(id) {
      const rawDevice = await deviceService.getById(id)
      const device = rawDevice ? this.smoothDevice(rawDevice) : rawDevice
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

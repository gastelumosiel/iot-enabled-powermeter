export const mockDevices = [
  {
    id: 'DEV001',
    device_id: 'DEV001',
    name: 'Aire Acondicionado',
    icon: 'air',
    timestamp: new Date().toISOString(),
    vrms: 220.0,
    irms: 5.78,
    active_power: 1280,
    reactive_power: 124,
    apparent_power: 1275,
    power_factor: 0.98,
    phase: 0.0,
    frequency: 60.0,
    energy_kwh: 30.73,
    status: 'online',
  },
  {
    id: 'DEV002',
    device_id: 'DEV002',
    name: 'Refrigerador',
    icon: 'fridge',
    timestamp: new Date().toISOString(),
    vrms: 220.0,
    irms: 0.68,
    active_power: 150,
    reactive_power: 18,
    apparent_power: 154,
    power_factor: 0.96,
    phase: 2.8,
    frequency: 60.0,
    energy_kwh: 4.2,
    status: 'online',
  },
  {
    id: 'DEV003',
    device_id: 'DEV003',
    name: 'Computadora',
    icon: 'computer',
    timestamp: new Date().toISOString(),
    vrms: 220.0,
    irms: 1.36,
    active_power: 300,
    reactive_power: 34,
    apparent_power: 306,
    power_factor: 0.97,
    phase: 1.4,
    frequency: 60.0,
    energy_kwh: 7.15,
    status: 'online',
  },
]

export const mockCfeSummary = {
  accumulated_kwh: 42.08,
  configured_limit: 280,
  usage_percent: 15.03,
  remaining_kwh: 237.92,
}

export const mockProfile = {
  name: 'Usuario PowerLytix',
  email: 'usuario@powerlytix.com',
  devices_count: 3,
  cfe_rate: 'Domestica 1C',
  bimonthly_limit_kwh: 280,
  created_at: '2026-05-03T17:00:00.000Z',
}

export function withLiveNoise(devices) {
  return devices.map((device) => {
    const jitter = Math.round((Math.random() - 0.45) * (device.active_power * 0.08))
    const active = Math.max(0, device.active_power + jitter)
    return {
      ...device,
      timestamp: new Date().toISOString(),
      active_power: active,
      irms: +(active / device.vrms).toFixed(2),
      apparent_power: Math.round(active / Math.max(device.power_factor, 0.1)),
      reactive_power: Math.round(active * 0.1),
    }
  })
}

export function makePowerHistory(range = '24h') {
  const points = range === '30d' ? 30 : range === '7d' ? 7 : 24
  return Array.from({ length: points }, (_, index) => {
    const date = new Date(Date.now() - (points - index - 1) * (range === '24h' ? 3600000 : 86400000))
    return {
      label: range === '24h'
        ? date.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
        : date.toLocaleDateString('es-MX', { day: '2-digit', month: 'short' }),
      power: Math.round(1700 + Math.sin(index) * 80 + Math.random() * 120),
    }
  })
}

export function makeDeviceHistorySeries(devices = mockDevices, range = '24h', locale = 'es-MX') {
  const points = range === '30d' ? 30 : range === '7d' ? 7 : 24
  const step = range === '24h' ? 3600000 : 86400000
  const palette = ['#047857', '#10b981', '#34d399', '#0f766e', '#65a30d']

  return devices.map((device, deviceIndex) => ({
    id: device.device_id,
    name: device.name,
    color: palette[deviceIndex % palette.length],
    points: Array.from({ length: points }, (_, index) => {
      const date = new Date(Date.now() - (points - index - 1) * step)
      const wave = Math.sin(index * 0.7 + deviceIndex) * device.active_power * 0.12
      const drift = Math.cos(index * 0.35) * device.active_power * 0.05

      return {
        label: range === '24h'
          ? date.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' })
          : date.toLocaleDateString(locale, { day: '2-digit', month: 'short' }),
        power: Math.max(0, Math.round(device.active_power + wave + drift)),
      }
    }),
  }))
}

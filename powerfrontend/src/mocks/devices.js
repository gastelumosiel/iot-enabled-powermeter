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
    const powerFactor = Math.min(1, Math.max(0.72, Number(device.power_factor || 0.95) + (Math.random() - 0.5) * 0.02))
    const voltage = Math.max(105, Number(device.vrms || 220) + (Math.random() - 0.5) * 1.8)
    return {
      ...device,
      timestamp: new Date().toISOString(),
      active_power: active,
      vrms: +voltage.toFixed(1),
      irms: +(active / voltage).toFixed(2),
      power_factor: +powerFactor.toFixed(2),
      apparent_power: Math.round(active / Math.max(powerFactor, 0.1)),
      reactive_power: Math.round(active * (1 - powerFactor + 0.08)),
      phase: +(Number(device.phase || 0) + (Math.random() - 0.5) * 0.8).toFixed(1),
      frequency: +(Number(device.frequency || 60) + (Math.random() - 0.5) * 0.08).toFixed(2),
      energy_kwh: +(Number(device.energy_kwh || 0) + active / 1000 / 720).toFixed(3),
    }
  })
}

function rangeConfig(range = '24h') {
  const configs = {
    '1h': { points: 13, step: 5 * 60000, time: true },
    '8h': { points: 17, step: 30 * 60000, time: true },
    '24h': { points: 24, step: 60 * 60000, time: true },
    '7d': { points: 14, step: 12 * 60 * 60000, date: true },
    '30d': { points: 30, step: 24 * 60 * 60000, date: true },
    '3m': { points: 13, step: 7 * 24 * 60 * 60000, date: true },
    '6m': { points: 13, step: 14 * 24 * 60 * 60000, date: true },
    '12m': { points: 12, step: 30 * 24 * 60 * 60000, month: true },
  }
  return configs[range] || configs['24h']
}

function parameterValue(device, parameter = 'active_power') {
  const fallback = {
    active_power: device.active_power,
    reactive_power: device.reactive_power,
    apparent_power: device.apparent_power,
    vrms: device.vrms,
    irms: device.irms,
    power_factor: device.power_factor,
    frequency: device.frequency,
    phase: device.phase,
  }
  return Number(fallback[parameter] ?? device.active_power ?? 0)
}

function formatHistoryLabel(date, config, locale) {
  if (config.month) return date.toLocaleDateString(locale, { month: 'short', year: '2-digit' })
  if (config.date) return date.toLocaleDateString(locale, { day: '2-digit', month: 'short' })
  return date.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' })
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

export function makeDeviceHistorySeries(devices = mockDevices, range = '24h', locale = 'es-MX', parameter = 'active_power') {
  const config = rangeConfig(range)
  const palette = ['#047857', '#10b981', '#34d399', '#0f766e', '#65a30d']

  return devices.map((device, deviceIndex) => ({
    id: device.device_id,
    name: device.name,
    color: palette[deviceIndex % palette.length],
    points: Array.from({ length: config.points }, (_, index) => {
      const date = new Date(Date.now() - (config.points - index - 1) * config.step)
      const base = parameterValue(device, parameter)
      const scale = ['power_factor', 'frequency', 'phase'].includes(parameter) ? 0.012 : 0.12
      const wave = Math.sin(index * 0.7 + deviceIndex) * base * scale
      const drift = Math.cos(index * 0.35) * base * (scale / 2)
      const value = Math.max(0, +(base + wave + drift).toFixed(['power_factor', 'irms', 'phase', 'frequency', 'vrms'].includes(parameter) ? 2 : 0))

      return {
        label: formatHistoryLabel(date, config, locale),
        value,
        power: value,
      }
    }),
  }))
}

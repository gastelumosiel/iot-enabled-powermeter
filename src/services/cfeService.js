import { api } from './api'

const officialBase = 'https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas'

const fallbackTariffs = {
  domestic_1: {
    label: 'Tarifa 1',
    code: '1',
    monthlyLimit: 250,
    sourceUrl: `${officialBase}/Tarifa1.aspx`,
    blocks: [
      { key: 'basic', kwh: 75, price: 1.12 },
      { key: 'intermediate', kwh: 65, price: 1.36 },
      { key: 'excess', kwh: Infinity, price: 3.99 },
    ],
  },
  domestic_1a: {
    label: 'Tarifa 1A',
    code: '1A',
    monthlyLimit: 300,
    sourceUrl: `${officialBase}/Tarifa1A.aspx`,
    blocks: [
      { key: 'basic', kwh: 100, price: 1.01 },
      { key: 'intermediate', kwh: 50, price: 1.17 },
      { key: 'excess', kwh: Infinity, price: 4.0 },
    ],
  },
  domestic_1b: {
    label: 'Tarifa 1B',
    code: '1B',
    monthlyLimit: 400,
    sourceUrl: `${officialBase}/Tarifa1B.aspx`,
    blocks: [
      { key: 'basic', kwh: 125, price: 1.01 },
      { key: 'intermediate', kwh: 100, price: 1.21 },
      { key: 'excess', kwh: Infinity, price: 4.0 },
    ],
  },
  domestic_1c: {
    label: 'Tarifa 1C',
    code: '1C',
    monthlyLimit: 850,
    sourceUrl: `${officialBase}/Tarifa1C.aspx`,
    blocks: [
      { key: 'basic', kwh: 150, price: 1.01 },
      { key: 'intermediate', kwh: 150, price: 1.21 },
      { key: 'excess', kwh: Infinity, price: 4.0 },
    ],
  },
  domestic_1d: {
    label: 'Tarifa 1D',
    code: '1D',
    monthlyLimit: 1000,
    sourceUrl: `${officialBase}/Tarifa1D.aspx`,
    blocks: [
      { key: 'basic', kwh: 175, price: 1.01 },
      { key: 'intermediate', kwh: 225, price: 1.21 },
      { key: 'excess', kwh: Infinity, price: 4.0 },
    ],
  },
  domestic_1e: {
    label: 'Tarifa 1E',
    code: '1E',
    monthlyLimit: 2000,
    sourceUrl: `${officialBase}/Tarifa1E.aspx`,
    blocks: [
      { key: 'basic', kwh: 300, price: 0.98 },
      { key: 'intermediate', kwh: 450, price: 1.16 },
      { key: 'excess', kwh: Infinity, price: 4.0 },
    ],
  },
  domestic_1f: {
    label: 'Tarifa 1F',
    code: '1F',
    monthlyLimit: 2500,
    sourceUrl: `${officialBase}/Tarifa1F.aspx`,
    blocks: [
      { key: 'basic', kwh: 300, price: 0.98 },
      { key: 'intermediate', kwh: 900, price: 1.16 },
      { key: 'excess', kwh: Infinity, price: 4.0 },
    ],
  },
}

async function fallback(callback, waitMs = 550) {
  try {
    return await Promise.race([
      callback(),
      new Promise((resolve) => setTimeout(() => resolve(null), waitMs)),
    ])
  } catch {
    return null
  }
}

export const cfeService = {
  localTariff(tariff) {
    return fallbackTariffs[tariff] || fallbackTariffs.domestic_1c
  },
  tariffOptions() {
    return Object.entries(fallbackTariffs).map(([value, tariff]) => ({
      value,
      label: tariff.label,
      monthlyLimit: tariff.monthlyLimit,
      sourceUrl: tariff.sourceUrl,
    }))
  },
  async tariff({ tariff, periodStart }) {
    const response = await fallback(() => api.get('/api/cfe/tariffs/', { params: { tariff, period_start: periodStart } }))
    return response?.data || fallbackTariffs[tariff] || fallbackTariffs.domestic_1c
  },
}

export const EMA_ALPHA = 0.35

export const EMA_FIELDS = [
  'vrms',
  'irms',
  'active_power',
  'reactive_power',
  'apparent_power',
  'power_factor',
  'phase',
  'frequency',
]

export function applyEmaFilter(previous, next, alpha = EMA_ALPHA) {
  if (next?.status === 'offline') {
    return EMA_FIELDS.reduce((device, field) => {
      device[field] = 0
      return device
    }, { ...next })
  }

  if (!previous) return { ...next }

  return EMA_FIELDS.reduce((device, field) => {
    const nextValue = Number(next?.[field])
    const previousValue = Number(previous?.[field])
    if (!Number.isFinite(nextValue) || !Number.isFinite(previousValue)) return device

    device[field] = alpha * nextValue + (1 - alpha) * previousValue
    return device
  }, { ...next })
}

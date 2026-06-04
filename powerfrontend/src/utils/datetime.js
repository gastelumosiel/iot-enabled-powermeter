export const APP_TIME_ZONE = 'America/Tijuana'

export function formatAppTime(value, locale) {
  return value
    ? new Date(value).toLocaleTimeString(locale, { timeZone: APP_TIME_ZONE })
    : ''
}

export function formatAppDate(value, locale, options = {}) {
  return value
    ? new Date(value).toLocaleDateString(locale, { timeZone: APP_TIME_ZONE, ...options })
    : ''
}

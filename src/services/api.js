import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 1800,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('powerlytix_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'
import WebApp from '@twa-dev/sdk'

const MOCK_TELEGRAM_USER = JSON.stringify({
  id: 123,
  username: 'Навигатор',
  first_name: 'Тест',
})

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const user = WebApp.initDataUnsafe?.user
  if (user) {
    config.headers['X-Telegram-User'] = JSON.stringify({
      id: user.id,
      username: user.username || '',
      first_name: user.first_name || '',
    })
  } else {
    config.headers['X-Telegram-User'] = MOCK_TELEGRAM_USER
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const { data } = await api.get<T>(url, config)
  return data
}

export async function post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.post<T>(url, data, config)
  return response.data
}

export async function patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.patch<T>(url, data, config)
  return response.data
}

/** Предзагрузка изображения для кэширования */
export function preloadImage(url: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve()
    img.onerror = reject
    img.src = url
  })
}

export default api

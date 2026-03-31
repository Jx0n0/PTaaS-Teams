import axios from 'axios'

const ACCESS_KEY = 'ptaas_access_token'
const REFRESH_KEY = 'ptaas_refresh_token'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
})

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY)
}

export function setTokens(access, refresh) {
  localStorage.setItem(ACCESS_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem(REFRESH_KEY)
      if (refresh) {
        try {
          const { data } = await axios.post(`${apiClient.defaults.baseURL}/api/v1/auth/refresh`, { refresh })
          setTokens(data.access, refresh)
          original.headers.Authorization = `Bearer ${data.access}`
          return apiClient(original)
        } catch {
          clearTokens()
        }
      }
    }
    return Promise.reject(error)
  }
)

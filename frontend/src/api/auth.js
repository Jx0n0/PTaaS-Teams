import { apiClient } from './client'

export const login = (payload) => apiClient.post('/api/v1/auth/login', payload)
export const me = () => apiClient.get('/api/v1/auth/me')
export const changePassword = (payload) => apiClient.post('/api/v1/auth/change-password', payload)

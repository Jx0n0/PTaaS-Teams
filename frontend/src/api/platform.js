import { apiClient } from './client'

export const fetchUsers = () => apiClient.get('/api/v1/users/')
export const createUser = (payload) => apiClient.post('/api/v1/users/', payload)

export const fetchRoles = () => apiClient.get('/api/v1/roles/')
export const createRole = (payload) => apiClient.post('/api/v1/roles/', payload)

export const fetchUserRoles = () => apiClient.get('/api/v1/user-roles/')
export const createUserRole = (payload) => apiClient.post('/api/v1/user-roles/', payload)

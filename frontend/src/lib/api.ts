import axios from 'axios'
import { Project, ApiResponse, ApiKey } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

export const projectsApi = {
  // Get all projects
  getAll: async (): Promise<Project[]> => {
    const response = await api.get<ApiResponse<Project[]>>('/projects')
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to fetch projects')
    }
    return response.data.data || []
  },

  // Get a single project
  get: async (id: string): Promise<Project> => {
    const response = await api.get<ApiResponse<Project>>(`/projects/${id}`)
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to fetch project')
    }
    return response.data.data!
  },

  // Create a new project
  create: async (data: { name: string; description?: string }): Promise<Project> => {
    const response = await api.post<ApiResponse<Project>>('/projects', data)
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to create project')
    }
    return response.data.data!
  },

  // Update a project
  update: async (id: string, data: { name?: string; description?: string }): Promise<Project> => {
    const response = await api.put<ApiResponse<Project>>(`/projects/${id}`, data)
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to update project')
    }
    return response.data.data!
  },

  // Delete a project
  delete: async (id: string): Promise<void> => {
    const response = await api.delete<ApiResponse>(`/projects/${id}`)
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to delete project')
    }
  },
}

export const settingsApi = {
  // Get all API keys
  getApiKeys: async (): Promise<ApiKey[]> => {
    const response = await api.get<ApiResponse<{ api_keys: ApiKey[] }>>('/settings/api-keys')
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to fetch API keys')
    }
    return response.data.data?.api_keys || []
  },

  // Update API keys
  updateApiKeys: async (apiKeys: { id: string; value: string }[]): Promise<void> => {
    const response = await api.post<ApiResponse>('/settings/api-keys', { api_keys: apiKeys })
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to update API keys')
    }
  },

  // Delete an API key
  deleteApiKey: async (keyId: string): Promise<void> => {
    const response = await api.delete<ApiResponse>(`/settings/api-keys/${keyId}`)
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to delete API key')
    }
  },

  // Validate an API key
  validateApiKey: async (keyId: string, value: string): Promise<{ valid: boolean; message: string }> => {
    const response = await api.post<ApiResponse<{ valid: boolean; message: string }>>('/settings/api-keys/validate', {
      key_id: keyId,
      value: value
    })
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to validate API key')
    }
    return response.data.data!
  },
}

// Named export for chats.ts and other modules
export { api }

export default api
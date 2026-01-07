import axios from 'axios'
import { Project, ApiResponse } from '@/types'

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

export default api
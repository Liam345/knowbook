export interface Project {
  id: string
  name: string
  description: string
  created_at: string
  updated_at: string
  last_opened: string
  stats: {
    sources_count: number
    chats_count: number
    total_size: number
  }
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
}
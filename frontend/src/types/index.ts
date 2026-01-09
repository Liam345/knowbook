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

export interface Source {
  id: string
  name: string
  description: string
  original_name: string
  file_path: string
  file_size: number
  file_type: string
  category: string
  status: 'uploaded' | 'processing' | 'embedding' | 'ready' | 'failed'
  active: boolean
  created_at: string
  updated_at: string
  processing_info?: Record<string, any>
  embedding_info?: Record<string, any>
  summary_info?: Record<string, any>
}

export interface ApiKey {
  id: string
  name: string
  description: string
  category: 'ai' | 'storage' | 'utility'
  required?: boolean
  value: string
  is_set: boolean
}
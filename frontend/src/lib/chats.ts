/**
 * Chat API Client - handles all chat-related API calls
 *
 * Educational Note: This module provides a clean interface to the chat endpoints.
 * It handles the request/response flow for chat management and messaging.
 */

import { api } from './api'
import type { Chat, ChatMetadata, Message } from '../types'

export interface CreateChatRequest {
  title?: string
}

export interface SendMessageRequest {
  message: string
}

export interface SendMessageResponse {
  success: boolean
  user_message: Message
  assistant_message: Message
}

export interface UpdateChatRequest {
  title: string
}

export interface CitationContent {
  chunk_id: string
  content: string
  source_name: string
  source_id: string
  page_number: number
  chunk_index: number
}

export interface TranscriptionConfig {
  websocket_url: string
  model_id: string
  sample_rate: number
  encoding: string
}

/**
 * Chat API functions
 */
export const chatsAPI = {
  /**
   * List all chats for a project
   */
  async listChats(projectId: string): Promise<ChatMetadata[]> {
    const response = await api.get(`/projects/${projectId}/chats`)
    return response.data.chats || []
  },

  /**
   * Create a new chat
   */
  async createChat(projectId: string, data: CreateChatRequest = {}): Promise<Chat> {
    const response = await api.post(`/projects/${projectId}/chats`, data)
    return response.data.chat
  },

  /**
   * Get a specific chat with all messages
   */
  async getChat(projectId: string, chatId: string): Promise<Chat> {
    const response = await api.get(`/projects/${projectId}/chats/${chatId}`)
    return response.data.chat
  },

  /**
   * Update a chat (rename)
   */
  async updateChat(projectId: string, chatId: string, data: UpdateChatRequest): Promise<Chat> {
    const response = await api.put(`/projects/${projectId}/chats/${chatId}`, data)
    return response.data.chat
  },

  /**
   * Delete a chat
   */
  async deleteChat(projectId: string, chatId: string): Promise<void> {
    await api.delete(`/projects/${projectId}/chats/${chatId}`)
  },

  /**
   * Send a message and get AI response
   */
  async sendMessage(projectId: string, chatId: string, data: SendMessageRequest): Promise<SendMessageResponse> {
    const response = await api.post(`/projects/${projectId}/chats/${chatId}/messages`, data)
    return {
      success: response.data.success,
      user_message: response.data.user_message,
      assistant_message: response.data.assistant_message
    }
  },

  /**
   * Get citation content for hover display
   */
  async getCitationContent(projectId: string, chunkId: string): Promise<CitationContent> {
    const response = await api.get(`/projects/${projectId}/citations/${chunkId}`)
    return response.data.citation
  },

  /**
   * Get WebSocket config for voice transcription
   */
  async getTranscriptionConfig(): Promise<TranscriptionConfig> {
    const response = await api.get('/transcription/config')
    return {
      websocket_url: response.data.websocket_url,
      model_id: response.data.model_id,
      sample_rate: response.data.sample_rate,
      encoding: response.data.encoding,
    }
  },

  /**
   * Check if ElevenLabs transcription is configured
   */
  async isTranscriptionConfigured(): Promise<boolean> {
    try {
      const response = await api.get('/transcription/status')
      return response.data.success && response.data.configured
    } catch {
      return false
    }
  }
}

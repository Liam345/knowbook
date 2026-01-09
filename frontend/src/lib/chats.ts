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

/**
 * Chat API functions
 */
export const chatsAPI = {
  /**
   * List all chats for a project
   */
  async listChats(projectId: string): Promise<ChatMetadata[]> {
    const response = await api.get(`/projects/${projectId}/chats`)
    return response.chats || []
  },

  /**
   * Create a new chat
   */
  async createChat(projectId: string, data: CreateChatRequest = {}): Promise<Chat> {
    const response = await api.post(`/projects/${projectId}/chats`, data)
    return response.chat
  },

  /**
   * Get a specific chat with all messages
   */
  async getChat(projectId: string, chatId: string): Promise<Chat> {
    const response = await api.get(`/projects/${projectId}/chats/${chatId}`)
    return response.chat
  },

  /**
   * Update a chat (rename)
   */
  async updateChat(projectId: string, chatId: string, data: UpdateChatRequest): Promise<Chat> {
    const response = await api.put(`/projects/${projectId}/chats/${chatId}`, data)
    return response.chat
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
      success: response.success,
      user_message: response.user_message,
      assistant_message: response.assistant_message
    }
  }
}
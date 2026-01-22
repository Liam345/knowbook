/**
 * ChatPanel Component
 * Educational Note: Main orchestrator for the chat interface.
 * Handles chat state, API interactions, and UI rendering.
 * Supports citations with hover cards for source references.
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  CaretDown,
  PaperPlaneTilt,
  ChatCircle,
  Plus,
  Trash,
  Microphone
} from '@phosphor-icons/react'
import { chatsAPI } from '@/lib/chats'
import type { Chat as ChatType, ChatMetadata, Project } from '@/types'
import { useToast } from '@/components/ui/toast'
import { parseCitations, parseChunkId } from '@/lib/citations'
import { CitationBadge } from '@/components/chat/CitationBadge'
import { useVoiceRecording } from '@/hooks/useVoiceRecording'

interface ChatPanelProps {
  project: Project
}

/**
 * MessageContent Component
 * Renders message text with citation badges
 */
function MessageContent({ content, projectId }: { content: string; projectId: string }) {
  // Parse citations from content
  const { uniqueCitations, markerToNumber } = useMemo(
    () => parseCitations(content),
    [content]
  )

  // If no citations, just render plain text
  if (uniqueCitations.length === 0) {
    return <div className="whitespace-pre-wrap">{content}</div>
  }

  // Split content and render with citation badges
  const parts: React.ReactNode[] = []
  const regex = /\[\[cite:([a-zA-Z0-9_-]+_page_\d+_chunk_\d+)\]\]/g
  let lastIndex = 0
  let match

  // Reset regex
  regex.lastIndex = 0

  while ((match = regex.exec(content)) !== null) {
    // Add text before citation
    if (match.index > lastIndex) {
      parts.push(
        <span key={`text-${lastIndex}`}>
          {content.slice(lastIndex, match.index)}
        </span>
      )
    }

    // Add citation badge
    const fullMarker = match[0]
    const chunkId = match[1]
    const citationNumber = markerToNumber.get(fullMarker) || 0
    const parsed = parseChunkId(chunkId)

    if (parsed) {
      parts.push(
        <CitationBadge
          key={`cite-${match.index}`}
          citationNumber={citationNumber}
          chunkId={chunkId}
          sourceId={parsed.sourceId}
          pageNumber={parsed.pageNumber}
          projectId={projectId}
        />
      )
    }

    lastIndex = regex.lastIndex
  }

  // Add remaining text
  if (lastIndex < content.length) {
    parts.push(
      <span key={`text-${lastIndex}`}>
        {content.slice(lastIndex)}
      </span>
    )
  }

  return <div className="whitespace-pre-wrap">{parts}</div>
}

export default function ChatPanel({ project }: ChatPanelProps) {
  // Chat state
  const [message, setMessage] = useState('')
  const [activeChat, setActiveChat] = useState<ChatType | null>(null)
  const [showChatList, setShowChatList] = useState(false)
  const [allChats, setAllChats] = useState<ChatMetadata[]>([])
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Toast hook
  const { success, error } = useToast()

  // Voice recording hook
  const {
    isRecording,
    partialTranscript,
    transcriptionConfigured,
    startRecording,
    stopRecording,
  } = useVoiceRecording({
    onError: error,
    onTranscriptCommit: useCallback((text: string) => {
      // Append committed text to message
      setMessage((prev) => {
        if (prev && !prev.endsWith(' ')) {
          return prev + ' ' + text
        }
        return prev + text
      })
    }, []),
  })

  /**
   * Toggle recording on mic click
   */
  const handleMicClick = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  /**
   * Load all chats when component mounts
   */
  useEffect(() => {
    loadChats()
  }, [project.id])

  /**
   * Scroll to bottom when messages change
   */
  useEffect(() => {
    scrollToBottom()
  }, [activeChat?.messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  /**
   * Load chats for the project
   */
  const loadChats = async () => {
    try {
      setLoading(true)
      const chats = await chatsAPI.listChats(project.id)
      setAllChats(chats)

      // If there's at least one chat, load the most recent one
      if (chats.length > 0) {
        const mostRecent = chats.sort((a, b) => 
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        )[0]
        await loadChat(mostRecent.id)
      }
    } catch (err) {
      console.error('Error loading chats:', err)
      error('Failed to load chats')
    } finally {
      setLoading(false)
    }
  }

  /**
   * Load a specific chat
   */
  const loadChat = async (chatId: string) => {
    try {
      const chat = await chatsAPI.getChat(project.id, chatId)
      setActiveChat(chat)
      setShowChatList(false)
    } catch (err) {
      console.error('Error loading chat:', err)
      error('Failed to load chat')
    }
  }

  /**
   * Create a new chat
   */
  const createNewChat = async () => {
    try {
      const chat = await chatsAPI.createChat(project.id, { title: 'New Chat' })
      setActiveChat(chat)
      setAllChats(prev => [{ ...chat, studio_signals: undefined }, ...prev])
      setShowChatList(false)
    } catch (err) {
      console.error('Error creating chat:', err)
      error('Failed to create chat')
    }
  }

  /**
   * Send a message
   */
  const sendMessage = async () => {
    if (!message.trim() || !activeChat || sending) return

    try {
      setSending(true)
      const messageText = message.trim()
      setMessage('')

      const response = await chatsAPI.sendMessage(project.id, activeChat.id, {
        message: messageText
      })

      // Update the active chat with new messages
      if (response.success) {
        setActiveChat(prev => prev ? {
          ...prev,
          messages: [...prev.messages, response.user_message, response.assistant_message],
          message_count: prev.message_count + 2,
          last_message_at: response.assistant_message.timestamp,
          updated_at: response.assistant_message.timestamp
        } : null)

        // Update the chat in the list
        setAllChats(prev => prev.map(chat => 
          chat.id === activeChat.id 
            ? { ...chat, message_count: chat.message_count + 2, last_message_at: response.assistant_message.timestamp }
            : chat
        ))
      }
    } catch (err) {
      console.error('Error sending message:', err)
      error('Failed to send message')
    } finally {
      setSending(false)
    }
  }

  /**
   * Handle Enter key press
   */
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  /**
   * Delete a chat
   */
  const deleteChat = async (chatId: string) => {
    if (!confirm('Are you sure you want to delete this chat?')) return

    try {
      await chatsAPI.deleteChat(project.id, chatId)
      setAllChats(prev => prev.filter(chat => chat.id !== chatId))
      
      if (activeChat?.id === chatId) {
        setActiveChat(null)
        // Load another chat if available
        const remainingChats = allChats.filter(chat => chat.id !== chatId)
        if (remainingChats.length > 0) {
          await loadChat(remainingChats[0].id)
        }
      }
      
      success('Chat deleted successfully')
    } catch (err) {
      console.error('Error deleting chat:', err)
      error('Failed to delete chat')
    }
  }

  /**
   * Format timestamp for display
   */
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  if (loading) {
    return (
      <div className="flex-1 flex flex-col">
        <div className="border-b p-4">
          <h2 className="font-semibold">Chat</h2>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-muted-foreground">Loading chats...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Chat Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ChatCircle size={20} />
            <h2 className="font-semibold">Chat</h2>
          </div>
          <div className="flex items-center gap-2">
            {/* Chat Selector */}
            {allChats.length > 0 && (
              <div className="relative">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowChatList(!showChatList)}
                  className="flex items-center gap-2"
                >
                  <span className="truncate max-w-32">
                    {activeChat?.title || 'Select Chat'}
                  </span>
                  <CaretDown size={16} />
                </Button>
                
                {showChatList && (
                  <div className="absolute top-full right-0 mt-2 w-64 bg-background border rounded-lg shadow-lg z-10 max-h-64 overflow-y-auto">
                    {allChats.map((chat) => (
                      <div key={chat.id} className="flex items-center hover:bg-muted">
                        <button
                          onClick={() => loadChat(chat.id)}
                          className="flex-1 p-3 text-left text-sm"
                        >
                          <div className="font-medium truncate">{chat.title}</div>
                          <div className="text-xs text-muted-foreground">
                            {chat.message_count} messages
                          </div>
                        </button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={(e) => {
                            e.stopPropagation()
                            deleteChat(chat.id)
                          }}
                          className="h-8 w-8 mr-2"
                        >
                          <Trash size={14} />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {/* New Chat Button */}
            <Button variant="ghost" size="icon" onClick={createNewChat}>
              <Plus size={16} />
            </Button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4">
        {!activeChat ? (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <ChatCircle size={48} className="mx-auto mb-4 text-muted-foreground" />
              <p className="mb-2">No chat selected</p>
              <Button onClick={createNewChat} variant="outline">
                <Plus size={16} className="mr-2" />
                Start New Chat
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {activeChat.messages.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>Start a conversation</p>
                <p className="text-sm">Ask questions about your sources</p>
              </div>
            ) : (
              activeChat.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    {msg.role === 'assistant' ? (
                      <MessageContent
                        content={typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
                        projectId={project.id}
                      />
                    ) : (
                      <div className="whitespace-pre-wrap">
                        {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
                      </div>
                    )}
                    <div className={`text-xs mt-1 ${msg.role === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                      {formatTimestamp(msg.timestamp)}
                    </div>
                  </div>
                </div>
              ))
            )}
            {sending && (
              <div className="flex justify-start">
                <div className="max-w-[80%] rounded-lg p-3 bg-muted">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <div className="animate-pulse">Thinking...</div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Message Input */}
      {activeChat && (
        <div className="border-t p-4">
          <div className="flex gap-2 items-end">
            {/* Microphone Button */}
            <button
              type="button"
              onClick={handleMicClick}
              disabled={sending || !transcriptionConfigured}
              className={`flex-shrink-0 p-2 rounded-full transition-colors ${
                isRecording
                  ? 'bg-red-500 text-white animate-pulse'
                  : transcriptionConfigured
                  ? 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  : 'text-muted-foreground/50 cursor-not-allowed'
              }`}
              title={
                !transcriptionConfigured
                  ? 'Voice input disabled - ElevenLabs API key not configured'
                  : isRecording
                  ? 'Stop recording'
                  : 'Start voice input'
              }
            >
              <Microphone size={18} />
            </button>

            <Textarea
              value={
                partialTranscript
                  ? message + (message && !message.endsWith(' ') ? ' ' : '') + partialTranscript
                  : message
              }
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder={
                isRecording
                  ? 'Listening...'
                  : !transcriptionConfigured
                  ? 'Ask about your sources... (voice disabled - set API key)'
                  : 'Ask about your sources... (Shift+Enter for new line)'
              }
              className="flex-1 min-h-[2.5rem] max-h-32 resize-none"
              disabled={sending || isRecording}
            />
            <Button
              onClick={sendMessage}
              disabled={!message.trim() || sending || isRecording}
              size="icon"
            >
              <PaperPlaneTilt size={16} />
            </Button>
          </div>
          <div className="text-xs text-muted-foreground mt-2">
            {isRecording ? (
              <span className="text-red-500">Recording... Click microphone to stop</span>
            ) : (
              'Press Enter to send, Shift+Enter for new line'
            )}
          </div>
        </div>
      )}
    </div>
  )
}
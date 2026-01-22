/**
 * useVoiceRecording Hook
 *
 * Educational Note: Real-time speech-to-text via ElevenLabs WebSocket.
 * Backend generates single-use tokens (15 min expiry), frontend connects directly.
 * Audio captured via AudioWorklet, converted to 16-bit PCM base64.
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { chatsAPI } from '@/lib/chats'

interface UseVoiceRecordingOptions {
  onError: (message: string) => void
  onTranscriptCommit: (text: string) => void
}

interface UseVoiceRecordingReturn {
  isRecording: boolean
  partialTranscript: string
  transcriptionConfigured: boolean
  startRecording: () => Promise<void>
  stopRecording: () => void
}

export function useVoiceRecording({
  onError,
  onTranscriptCommit,
}: UseVoiceRecordingOptions): UseVoiceRecordingReturn {
  const [isRecording, setIsRecording] = useState(false)
  const [partialTranscript, setPartialTranscript] = useState('')
  const [transcriptionConfigured, setTranscriptionConfigured] = useState(false)

  // Refs for cleanup
  const websocketRef = useRef<WebSocket | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const workletNodeRef = useRef<AudioWorkletNode | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const commitProcessedRef = useRef(false)

  /**
   * Check if ElevenLabs API is configured on mount
   */
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const configured = await chatsAPI.isTranscriptionConfigured()
        setTranscriptionConfigured(configured)
      } catch {
        setTranscriptionConfigured(false)
      }
    }
    checkStatus()
  }, [])

  /**
   * Start audio capture with AudioWorklet
   */
  const startAudioCapture = useCallback(
    async (sampleRate: number) => {
      try {
        // Request microphone with preprocessing
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            channelCount: 1,
            sampleRate: sampleRate,
            echoCancellation: true,
            noiseSuppression: true,
          },
        })
        mediaStreamRef.current = stream

        // Create AudioContext
        const audioContext = new AudioContext({ sampleRate })
        audioContextRef.current = audioContext

        // Create inline AudioWorklet (PCM processor)
        const workletCode = `
          class PCMProcessor extends AudioWorkletProcessor {
            constructor() {
              super();
              this.buffer = [];
              this.bufferSize = 4096; // ~0.25 sec at 16kHz
            }
            process(inputs) {
              const input = inputs[0];
              if (input && input[0]) {
                const float32 = input[0];
                // Convert Float32 (-1 to 1) to Int16 PCM
                for (let i = 0; i < float32.length; i++) {
                  const s = Math.max(-1, Math.min(1, float32[i]));
                  const int16 = s < 0 ? s * 0x8000 : s * 0x7FFF;
                  this.buffer.push(int16);
                }
                // Send when buffer full
                if (this.buffer.length >= this.bufferSize) {
                  const int16Array = new Int16Array(this.buffer);
                  this.port.postMessage(int16Array.buffer, [int16Array.buffer]);
                  this.buffer = [];
                }
              }
              return true;
            }
          }
          registerProcessor('pcm-processor', PCMProcessor);
        `

        // Create blob URL for worklet
        const blob = new Blob([workletCode], { type: 'application/javascript' })
        const url = URL.createObjectURL(blob)

        // Add worklet and connect audio graph
        await audioContext.audioWorklet.addModule(url)
        URL.revokeObjectURL(url)

        const source = audioContext.createMediaStreamSource(stream)
        const workletNode = new AudioWorkletNode(audioContext, 'pcm-processor')
        workletNodeRef.current = workletNode

        // Send audio to WebSocket as base64 JSON
        workletNode.port.onmessage = (event) => {
          if (websocketRef.current?.readyState === WebSocket.OPEN) {
            const bytes = new Uint8Array(event.data)
            const audioBase64 = btoa(String.fromCharCode(...bytes))
            websocketRef.current.send(
              JSON.stringify({
                message_type: 'input_audio_chunk',
                audio_base_64: audioBase64,
                sample_rate: sampleRate,
              })
            )
          }
        }

        source.connect(workletNode)
        workletNode.connect(audioContext.destination)
      } catch (err) {
        console.error('Failed to start audio capture:', err)
        onError('Failed to access microphone')
        throw err
      }
    },
    [onError]
  )

  /**
   * Start recording
   */
  const startRecording = useCallback(async () => {
    if (isRecording) return

    try {
      setPartialTranscript('')
      commitProcessedRef.current = false

      // Fetch fresh WebSocket config (single-use token)
      const config = await chatsAPI.getTranscriptionConfig()

      // Connect to ElevenLabs WebSocket
      const ws = new WebSocket(config.websocket_url)
      websocketRef.current = ws

      ws.onopen = () => {
        // Wait for session_started before audio capture
      }

      ws.onmessage = async (event) => {
        const data = JSON.parse(event.data)

        if (data.message_type === 'session_started') {
          // Start capturing audio
          await startAudioCapture(config.sample_rate)
          setIsRecording(true)
        } else if (data.message_type === 'partial_transcript') {
          setPartialTranscript(data.text || '')
        } else if (data.message_type === 'committed_transcript') {
          if (!commitProcessedRef.current && data.text) {
            commitProcessedRef.current = true
            onTranscriptCommit(data.text)
            setPartialTranscript('')
          }
        } else if (data.message_type === 'auth_error') {
          onError('Authentication error')
          ws.close()
        }
      }

      ws.onerror = () => {
        onError('WebSocket connection failed')
        setIsRecording(false)
      }

      ws.onclose = () => {
        setIsRecording(false)
      }
    } catch (err) {
      console.error('Failed to start recording:', err)
      onError('Failed to start recording')
      setIsRecording(false)
    }
  }, [isRecording, startAudioCapture, onError, onTranscriptCommit])

  /**
   * Stop recording
   */
  const stopRecording = useCallback(() => {
    const currentPartial = partialTranscript

    // Disconnect audio nodes
    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect()
      workletNodeRef.current = null
    }

    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop())
      mediaStreamRef.current = null
    }

    // Send manual commit to ElevenLabs
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      websocketRef.current.send(
        JSON.stringify({
          message_type: 'input_audio_chunk',
          audio_base_64: '',
          commit: true,
          sample_rate: 16000,
        })
      )

      // Wait for committed_transcript before closing
      setTimeout(() => {
        // Fallback: if no commit received, use partial
        if (currentPartial && !commitProcessedRef.current) {
          onTranscriptCommit(currentPartial)
        }
        if (websocketRef.current) {
          websocketRef.current.close()
          websocketRef.current = null
        }
        setPartialTranscript('')
      }, 500)
    } else {
      setPartialTranscript('')
    }

    setIsRecording(false)
  }, [partialTranscript, onTranscriptCommit])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close()
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop())
      }
    }
  }, [])

  return {
    isRecording,
    partialTranscript,
    transcriptionConfigured,
    startRecording,
    stopRecording,
  }
}

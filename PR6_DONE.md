# Module 6: Chat System - Enhanced

**Status**: COMPLETE

## Overview

Module 6 implements the enhanced chat system with RAG (Retrieval Augmented Generation), memory system, citations, and voice input support. This module transforms the basic chat into a full-featured AI assistant that can search sources, remember context, and accept voice input.

## Components Implemented

### Backend

#### 1. Tool Definitions (`/backend/app/tools/`)
- `search_sources.json` - Schema for source search tool
- `store_memory.json` - Schema for memory storage tool
- `studio_signal.json` - Schema for studio signals tool
- `analyze_csv.json` - Placeholder for CSV analysis tool
- `__init__.py` - Tool loader with `get_chat_tools()` function

#### 2. Tool Executors (`/backend/app/services/tool_executors/`)
- `source_search_executor.py` - Hybrid search (keyword + semantic)
  - Small sources (<1000 tokens): Returns all chunks
  - Large sources: Combines fuzzy keyword search + Pinecone semantic search
  - Deduplicates and formats results with chunk_ids
- `memory_executor.py` - Non-blocking memory storage
  - Returns immediately while background thread handles AI merge
  - Supports both user memory and project memory
- `studio_signal_executor.py` - Studio tool signals
  - Stores signals to chat JSON for UI display

#### 3. Memory Service (`/backend/app/services/memory_service.py`)
- User memory: Global across all projects
- Project memory: Project-specific, deleted with project
- AI-powered merge using Haiku model
- `build_memory_context()` for system prompt injection

#### 4. Citation Utilities (`/backend/app/utils/citation_utils.py`)
- Citation format: `[[cite:CHUNK_ID]]`
- Chunk ID format: `{source_id}_page_{N}_chunk_{M}`
- Functions: `extract_citations_from_text()`, `parse_chunk_id()`, `get_chunk_content()`, `convert_citations_to_numbered()`

#### 5. Updated Main Chat Service (`/backend/app/services/main_chat_service.py`)
- Full tool use loop with MAX_TOOL_ITERATIONS = 10
- Integrates all tool executors
- Builds system prompt with memory context and available sources
- Routes tool calls to appropriate executors

#### 6. Citation API Endpoint (`/backend/app/api/chats.py`)
- `GET /projects/<project_id>/citations/<chunk_id>` - Returns citation content for hover display

#### 7. Transcription API (`/backend/app/api/transcription/`)
- `GET /transcription/config` - Returns ElevenLabs WebSocket URL with single-use token
- `GET /transcription/status` - Checks if ElevenLabs is configured

#### 8. Transcription Service (`/backend/app/services/integrations/elevenlabs/`)
- `TranscriptionService` class
- Generates single-use tokens for client-side WebSocket connection
- Token-based auth keeps API key server-side

### Frontend

#### 1. Citation System
- `src/lib/citations.ts` - Citation parsing utilities
  - `parseCitations()` - Extract and number citations
  - `parseChunkId()` - Parse chunk ID components
  - `hasCitations()`, `stripCitations()`

- `src/components/chat/CitationBadge.tsx` - Citation hover card
  - Lazy loads content on hover
  - Uses Radix HoverCard component
  - Displays source name, page, and content

- Updated `ChatPanel.tsx`
  - `MessageContent` component with citation rendering
  - Parses `[[cite:CHUNK_ID]]` markers
  - Renders inline CitationBadge components

#### 2. Voice Input
- `src/hooks/useVoiceRecording.ts` - Voice recording hook
  - ElevenLabs WebSocket integration
  - AudioWorklet for low-latency PCM capture
  - Real-time partial transcript display
  - Automatic commit on voice activity detection

- Updated `ChatPanel.tsx`
  - Microphone button with recording state
  - Partial transcript display in textarea
  - Recording indicator and instructions

#### 3. New UI Components
- `src/components/ui/hover-card.tsx` - Radix HoverCard wrapper
- `src/components/ui/badge.tsx` - Badge component for citations

#### 4. API Updates
- `src/lib/chats.ts`
  - `getCitationContent()` - Fetch citation content
  - `getTranscriptionConfig()` - Get ElevenLabs WebSocket config
  - `isTranscriptionConfigured()` - Check if voice input available

## API Endpoints

### Chat Tools (via tool use)
- `search_sources` - Search project sources with keywords/query
- `store_memory` - Store user/project memory
- `studio_signal` - Signal studio tool opportunities

### REST Endpoints
- `GET /api/v1/projects/<id>/citations/<chunk_id>` - Citation content
- `GET /api/v1/transcription/config` - Voice WebSocket config
- `GET /api/v1/transcription/status` - Voice input availability

## Dependencies Added

### Frontend
- `@radix-ui/react-hover-card` - For citation hover cards

## Architecture Notes

### Hybrid Search Strategy
```
if source.token_count < 1000:
    → Return ALL chunks (small source, no search needed)
else:
    → Keyword search (fuzzy matching via difflib)
    → Semantic search (OpenAI embedding → Pinecone)
    → Combine, dedupe by chunk_id, return top 5
```

### Memory System
```
User requests "remember" → Claude calls store_memory tool
    → Memory executor returns immediately
    → Background thread: Haiku merges new + existing memory
    → Saved to JSON file
    → Included in next message's system prompt
```

### Citation Flow
```
Claude response: "Info here [[cite:abc123_page_5_chunk_2]]"
    → Frontend parses citations, assigns numbers [1], [2]
    → Renders CitationBadge inline
    → Hover → Lazy fetch GET /citations/{chunk_id}
    → Display source name, page, content in tooltip
```

### Voice Input Flow
```
User clicks mic → Frontend fetches /transcription/config
    → Gets single-use token embedded in WebSocket URL
    → Connects directly to ElevenLabs
    → AudioWorklet captures PCM audio
    → Streams to WebSocket
    → Partial transcripts update textarea
    → Final commit appends to message
```

## Testing

- Frontend TypeScript build: PASS
- All new components created and integrated
- Backend services with error handling

## Next Steps (Module 7+)

- Studio panel with content generation
- Audio/video overview generation
- Document generation (presentations, PRDs)
- Mind map generation

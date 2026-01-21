# PR #5: Module 5 - Source Management - Advanced
## AI-Powered Source Processing Complete

---

## Module Overview

**Module 5** implements the complete advanced source processing pipeline for KnowBook, enabling intelligent document extraction, text chunking, embedding generation, and multi-source support. This module transforms raw documents into searchable, AI-ready knowledge.

### What This Module Accomplishes

This PR implements the complete **source processing and embedding infrastructure** that enables KnowBook to extract and understand content from multiple source types:
- Token-based text chunking (~200 tokens per chunk)
- OpenAI embedding generation with text-embedding-3-small
- Pinecone vector storage with project-scoped namespaces
- YouTube transcript extraction
- Text and Word document processing
- URL and text paste source types
- Haiku-powered document summaries

---

## Architecture Implemented

### Backend Processing Infrastructure
```
backend/
├── app/
│   ├── api/
│   │   └── sources.py                     # Extended with URL/text endpoints
│   ├── services/
│   │   ├── source_service.py              # Extended with URL/text sources
│   │   ├── source_processing_service.py   # Processor routing and orchestration
│   │   ├── embedding_service.py           # Chunk → Embed → Store pipeline
│   │   ├── summary_service.py             # Haiku summary generation
│   │   ├── source_processing/
│   │   │   ├── text_processor.py          # Plain text and markdown
│   │   │   ├── docx_processor.py          # Word documents
│   │   │   └── youtube_processor.py       # YouTube transcripts
│   │   └── integrations/
│   │       ├── openai/
│   │       │   └── openai_service.py      # Embedding generation
│   │       ├── pinecone/
│   │       │   └── pinecone_service.py    # Vector storage
│   │       └── youtube/
│   │           └── youtube_service.py     # Transcript fetching
│   └── utils/
│       └── text/
│           ├── cleaning.py                # Text normalization
│           ├── page_markers.py            # Page marker format
│           ├── embedding_utils.py         # Token counting
│           ├── chunking.py                # Text segmentation
│           └── processed_output.py        # Output formatting
```

### Frontend Source Interface
```
frontend/
├── src/
│   ├── components/
│   │   └── SourceUploadDialog.tsx         # 3-tab interface (Upload/Link/Paste)
│   ├── lib/
│   │   └── api.ts                         # Extended sourcesApi
│   └── types/
│       └── index.ts                       # Source type with link fields
```

---

## Features Delivered

### Text Processing Pipeline
- **Token-Based Chunking**
  - ~200 tokens per chunk with tiktoken cl100k_base encoder
  - Sentence boundary splitting for natural chunk breaks
  - 20% margin tolerance for chunk sizes
  - Page-aware chunking preserving document structure

- **Standardized Output Format**
  - Page markers: `=== TYPE PAGE N of TOTAL ===`
  - Metadata header with processing info
  - Consistent format across all source types
  - Character and token count tracking

- **Text Cleaning**
  - Aggressive cleaning for embeddings
  - Whitespace normalization
  - Metadata header removal for chunks
  - Unicode handling

### Embedding Infrastructure
- **OpenAI Integration**
  - text-embedding-3-small model (1536 dimensions)
  - Batch processing (100 texts per batch)
  - Lazy client initialization
  - Error handling for API failures

- **Pinecone Integration**
  - Project-scoped namespaces
  - Upsert with source metadata
  - Query with optional source filtering
  - Delete by source ID

- **Summary Generation**
  - Claude Haiku for cost-effective summaries
  - Smart sampling (8 evenly distributed chunks)
  - Structured prompt for quality summaries
  - Fallback for API unavailability

### Source Type Support
- **Text Files (.txt, .md)**
  - Direct content extraction
  - UTF-8 encoding handling
  - Single-page format

- **Word Documents (.docx)**
  - python-docx extraction
  - Paragraph preservation
  - Structure-aware processing

- **YouTube Videos**
  - URL detection and video ID extraction
  - Transcript API integration
  - Timestamp-based page markers
  - Automatic name generation from video ID

- **URL Sources**
  - YouTube vs web URL detection
  - .link file storage format
  - Web scraping placeholder ready

- **Text Paste**
  - Direct text input support
  - Name-required validation
  - Immediate processing

### Placeholder Processors
Ready infrastructure for future implementation:
- PDF (Vision-based extraction)
- PPTX (Slide extraction)
- Images (Vision description)
- Audio (ElevenLabs transcription)
- CSV (Structured data)
- Research (Web agent)

---

## Technical Specifications

### API Endpoints Added
```
# URL Source Management
POST   /api/v1/projects/{id}/sources/url         # Add YouTube/web URL
POST   /api/v1/projects/{id}/sources/text        # Add pasted text

# Processed Content
GET    /api/v1/projects/{id}/sources/{id}/processed  # Get extracted text
```

### Data Models
```typescript
interface Source {
  id: string
  name: string
  description: string
  original_name: string
  file_path: string
  file_size: number
  file_type: string
  category: string
  status: 'uploaded' | 'processing' | 'embedding' | 'ready' | 'failed' | 'error'
  active: boolean
  created_at: string
  updated_at: string
  processing_info?: Record<string, any>
  embedding_info?: Record<string, any>
  summary_info?: Record<string, any>
  // Link source specific
  link_type?: 'youtube' | 'web'
  url?: string
}

interface Chunk {
  text: string
  page_number: number
  source_id: string
  chunk_id: string
  token_count?: number
  source_name?: string
}
```

### Processing Flow
```python
def process_source_pipeline(project_id: str, source_id: str):
    """
    Complete source processing pipeline:
    1. Load source metadata and raw file
    2. Route to type-specific processor
    3. Extract text content with page markers
    4. Save processed output to processed/{id}.txt
    5. Parse into chunks (~200 tokens each)
    6. Save chunk files to chunks/{source_id}/
    7. Generate embeddings via OpenAI
    8. Store vectors in Pinecone
    9. Generate summary via Haiku
    10. Update source status to 'ready'
    """
```

### File System Structure
```
data/projects/{project_id}/
├── sources/
│   ├── raw/
│   │   ├── {source_id}.txt          # Uploaded text files
│   │   ├── {source_id}.docx         # Uploaded Word docs
│   │   └── {source_id}.link         # URL source metadata
│   ├── processed/
│   │   └── {source_id}.txt          # Extracted text with markers
│   ├── chunks/
│   │   └── {source_id}/
│   │       ├── chunk_0.txt
│   │       ├── chunk_1.txt
│   │       └── ...
│   └── sources_index.json           # Source metadata index
```

---

## User Experience

### Three-Tab Source Dialog
1. **Upload Tab**: Drag-and-drop file upload
   - Supported formats display
   - File type validation
   - Size limit (50MB)
   - Category detection

2. **Link Tab**: URL source input
   - YouTube URL detection with icon change
   - Web page support (placeholder)
   - Optional custom name
   - Automatic name generation

3. **Paste Tab**: Direct text input
   - Required name field
   - Character count display
   - Large text area
   - Immediate processing

### Visual Design
- Tab-based interface with clear labels
- Icon indicators for source types
- Loading states during processing
- Error messages with guidance
- Responsive layout

---

## Testing Completed

### Backend Testing
- All Python imports successful
- Token counting verified (tiktoken)
- Page marker generation working
- Text chunking produces correct chunks
- YouTube URL detection accurate
- Flask routes registered correctly
- Processor routing table verified

### Integration Testing
- OpenAI service lazy initialization
- Pinecone service lazy initialization
- YouTube service URL parsing
- Source processing service routing
- Background thread processing

### Frontend Testing
- TypeScript compilation clean
- API types properly defined
- Source dialog renders correctly
- Tab switching works
- Form validation functional

---

## Dependencies Added

### Backend Dependencies
```python
# requirements.txt additions:
youtube-transcript-api==1.0.3    # YouTube transcript fetching
tiktoken                         # Token counting (already installed)
python-docx                      # Word document processing
openai                          # Embedding generation (already installed)
pinecone-client                 # Vector storage (already installed)
```

### Integration Services
- **OpenAI**: text-embedding-3-small for embeddings
- **Pinecone**: Vector database with namespaces
- **YouTube Transcript API**: Transcript extraction
- **Claude Haiku**: Summary generation

---

## Implementation Details

### Token Counting Strategy
```python
# Using tiktoken for fast local counting
import tiktoken
encoder = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(encoder.encode(text))

# Constants
CHUNK_TOKEN_TARGET = 200
CHUNK_MARGIN_PERCENT = 20  # Allow 160-240 tokens
```

### Chunking Algorithm
```python
def parse_processed_text(content: str, source_id: str, source_name: str) -> List[Chunk]:
    """
    1. Skip header section (before # ---)
    2. Find page markers
    3. Extract content between markers
    4. Split into sentences
    5. Build chunks up to target tokens
    6. Respect sentence boundaries
    7. Return list of Chunk objects
    """
```

### Embedding Pipeline
```python
class EmbeddingService:
    def process_embeddings(self, project_id, source_id, source_name):
        """
        1. Load processed text
        2. Check if embedding needed (token count > threshold)
        3. Parse into chunks
        4. Save chunk files
        5. Batch create embeddings (100 per batch)
        6. Format for Pinecone with metadata
        7. Upsert to Pinecone namespace
        8. Return embedding info
        """
```

### Processor Routing
```python
PROCESSOR_MAP = {
    '.txt': 'text',
    '.md': 'text',
    '.docx': 'docx',
    '.pdf': 'pdf',      # placeholder
    '.pptx': 'pptx',    # placeholder
    '.png': 'image',    # placeholder
    '.jpg': 'image',    # placeholder
    '.mp3': 'audio',    # placeholder
    '.csv': 'csv',      # placeholder
    '.link': 'link',    # YouTube implemented, web placeholder
    '.research': 'research'  # placeholder
}
```

---

## What's Next

### Module 6: Chat System - Enhanced
The processing foundation enables:
- **RAG Implementation**: Search embeddings for relevant context
- **Source Citations**: Reference specific chunks in responses
- **search_sources Tool**: AI-powered document querying

### Future Processor Implementation
Ready for completion:
- **PDF Processor**: Claude Vision for text extraction
- **Image Processor**: Claude Vision for description
- **Audio Processor**: ElevenLabs transcription
- **Web Agent**: Tavily search + content extraction

### Advanced Features
- **Hybrid Search**: Combine keyword and semantic search
- **Multi-modal RAG**: Images and audio in context
- **Incremental Updates**: Re-process changed sources

---

## Definition of Done

This module meets all acceptance criteria:

### Functional Requirements
- Users can add sources via file upload, URL, or text paste
- Text and Word documents are fully processed
- YouTube transcripts are extracted and embedded
- Processed content is viewable
- Sources show processing status

### Technical Requirements
- Token-based chunking at ~200 tokens
- OpenAI embeddings stored in Pinecone
- Background processing with status updates
- Lazy initialization for API clients
- Comprehensive error handling

### User Experience Requirements
- Three-tab dialog for source types
- YouTube URL auto-detection
- Processing status indicators
- Error messages with guidance

---

## Module 5 Complete!

The advanced source processing system of KnowBook is now fully functional for text-based sources and ready for RAG integration. This module successfully implements the extraction and embedding pipeline that will enable intelligent document-based conversations.

**Key Achievements:**
- Text Utilities: Token counting, chunking, page markers
- Embedding Pipeline: OpenAI + Pinecone integration
- Summary Generation: Haiku-powered document summaries
- YouTube Support: Full transcript extraction
- Multi-Source Types: Upload, URL, and paste support
- Extensible Architecture: Placeholder processors ready

**Ready to merge and move to Module 6: Chat System - Enhanced!**

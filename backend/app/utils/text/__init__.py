"""
Text processing utilities for KnowBook source management.

This module provides utilities for:
- Text cleaning and normalization
- Page marker generation and parsing
- Token counting and embedding decisions
- Text chunking for vector embeddings
- Processed output formatting
"""

from app.utils.text.cleaning import (
    clean_text_for_embedding,
    clean_chunk_text,
    normalize_whitespace
)

from app.utils.text.page_markers import (
    build_page_marker,
    find_all_markers,
    get_page_number,
    get_total_pages,
    PAGE_MARKER_PATTERN
)

from app.utils.text.embedding_utils import (
    count_tokens,
    count_tokens_api,
    needs_embedding,
    CHUNK_TOKEN_TARGET,
    CHUNK_MARGIN_PERCENT
)

from app.utils.text.processed_output import (
    build_processed_output,
    save_processed_text,
    load_processed_text,
    build_and_save_processed_output,
    parse_processed_header
)

from app.utils.text.chunking import (
    Chunk,
    parse_processed_text,
    parse_extracted_text,
    save_chunks_to_files,
    load_chunk_by_id,
    load_chunks_for_source,
    chunks_to_pinecone_format,
    delete_chunks_for_source
)

__all__ = [
    # Cleaning
    'clean_text_for_embedding',
    'clean_chunk_text',
    'normalize_whitespace',
    # Page markers
    'build_page_marker',
    'find_all_markers',
    'get_page_number',
    'get_total_pages',
    'PAGE_MARKER_PATTERN',
    # Embedding utils
    'count_tokens',
    'count_tokens_api',
    'needs_embedding',
    'CHUNK_TOKEN_TARGET',
    'CHUNK_MARGIN_PERCENT',
    # Processed output
    'build_processed_output',
    'save_processed_text',
    'load_processed_text',
    'build_and_save_processed_output',
    'parse_processed_header',
    # Chunking
    'Chunk',
    'parse_processed_text',
    'parse_extracted_text',
    'save_chunks_to_files',
    'load_chunk_by_id',
    'load_chunks_for_source',
    'chunks_to_pinecone_format',
    'delete_chunks_for_source',
]

"""
Text chunking utilities for KnowBook.

Provides token-based text segmentation for vector embeddings.
Target: ~200 tokens per chunk with sentence boundary splitting.
"""
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from app.utils.text.cleaning import clean_text_for_embedding
from app.utils.text.page_markers import extract_pages
from app.utils.text.embedding_utils import (
    count_tokens,
    CHUNK_TOKEN_TARGET,
    CHUNK_MAX_TOKENS,
    CHUNK_MIN_TOKENS
)


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    text: str
    page_number: int
    source_id: str
    source_name: str
    chunk_id: str
    chunk_index: int


def parse_processed_text(
    text: str,
    source_id: str,
    source_name: str
) -> List[Chunk]:
    """
    Parse processed text into chunks.

    Extracts content between page markers, cleans it, and splits
    into token-based chunks.

    Args:
        text: Full processed text with page markers
        source_id: Source UUID
        source_name: Display name for source

    Returns:
        List of Chunk objects
    """
    if not text:
        return []

    # Extract pages from processed text
    pages = extract_pages(text)
    if not pages:
        return []

    chunks = []
    global_chunk_index = 0

    for page_number, page_content in pages:
        # Clean the page content
        cleaned = clean_text_for_embedding(page_content)
        if not cleaned:
            continue

        # Split page into token-based chunks
        page_chunks = _split_text_into_token_chunks(cleaned)

        for chunk_text in page_chunks:
            global_chunk_index += 1
            chunk_id = f"{source_id}_page_{page_number}_chunk_{global_chunk_index}"

            chunk = Chunk(
                text=chunk_text,
                page_number=page_number,
                source_id=source_id,
                source_name=source_name,
                chunk_id=chunk_id,
                chunk_index=global_chunk_index
            )
            chunks.append(chunk)

    return chunks


def _split_text_into_token_chunks(text: str) -> List[str]:
    """
    Split text into chunks of approximately CHUNK_TOKEN_TARGET tokens.

    Strategy:
    1. If text fits in one chunk, return as-is
    2. Split at sentence boundaries near target size
    3. Fall back to word boundaries for long sentences

    Args:
        text: Cleaned text to split

    Returns:
        List of chunk strings
    """
    if not text:
        return []

    total_tokens = count_tokens(text)

    # If fits in single chunk, return as-is
    if total_tokens <= CHUNK_MAX_TOKENS:
        return [text]

    # Split into sentences
    sentences = _split_into_sentences(text)
    if not sentences:
        return [text]

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        # Handle very long sentences by splitting on words
        if sentence_tokens > CHUNK_MAX_TOKENS:
            # Flush current chunk first
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_tokens = 0

            # Split long sentence into word chunks
            word_chunks = _split_long_sentence(sentence)
            chunks.extend(word_chunks)
            continue

        # Check if adding this sentence would exceed target
        if current_tokens + sentence_tokens > CHUNK_TOKEN_TARGET:
            # If we have content, save it as a chunk
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_tokens = 0

        # Add sentence to current chunk
        current_chunk.append(sentence)
        current_tokens += sentence_tokens

    # Don't forget the last chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def _split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences.

    Uses regex to split on sentence-ending punctuation while
    handling common abbreviations.

    Args:
        text: Text to split

    Returns:
        List of sentences
    """
    if not text:
        return []

    # Split on sentence-ending punctuation followed by space
    # Handles: . ! ? and their combinations with quotes
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    sentences = re.split(sentence_pattern, text)

    # Clean up and filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences


def _split_long_sentence(sentence: str) -> List[str]:
    """
    Split a long sentence into chunks by word boundaries.

    Used as fallback when a sentence exceeds CHUNK_MAX_TOKENS.

    Args:
        sentence: Long sentence to split

    Returns:
        List of chunk strings
    """
    words = sentence.split()
    if not words:
        return []

    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_tokens = count_tokens(word)

        if current_tokens + word_tokens > CHUNK_TOKEN_TARGET:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_tokens = 0

        current_chunk.append(word)
        current_tokens += word_tokens

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def save_chunks_to_files(
    chunks: List[Chunk],
    chunks_dir: Path
) -> List[Path]:
    """
    Save chunks as individual text files.

    Each chunk file includes a metadata header followed by content.

    Args:
        chunks: List of Chunk objects
        chunks_dir: Base chunks directory (will create source_id subdir)

    Returns:
        List of paths to saved chunk files
    """
    if not chunks:
        return []

    saved_paths = []

    for chunk in chunks:
        # Create source-specific directory
        source_chunks_dir = chunks_dir / chunk.source_id
        source_chunks_dir.mkdir(parents=True, exist_ok=True)

        # Build chunk file content with metadata header
        header_lines = [
            f"# chunk_id: {chunk.chunk_id}",
            f"# page_number: {chunk.page_number}",
            f"# source_id: {chunk.source_id}",
            f"# source_name: {chunk.source_name}",
            f"# chunk_index: {chunk.chunk_index}",
            f"# character_count: {len(chunk.text)}",
            f"# token_count: {count_tokens(chunk.text)}",
            f"# created_at: {datetime.utcnow().isoformat()}",
            "# ---",
            "",
            chunk.text
        ]

        content = '\n'.join(header_lines)

        # Save chunk file
        file_path = source_chunks_dir / f"{chunk.chunk_id}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        saved_paths.append(file_path)

    return saved_paths


def load_chunk_by_id(
    chunk_id: str,
    chunks_dir: Path
) -> Optional[Dict[str, Any]]:
    """
    Load a chunk by its ID.

    Args:
        chunk_id: Chunk identifier (format: {source_id}_page_{n}_chunk_{m})
        chunks_dir: Base chunks directory

    Returns:
        Dictionary with chunk data or None if not found
    """
    # Extract source_id from chunk_id
    parts = chunk_id.split('_page_')
    if len(parts) < 2:
        return None

    source_id = parts[0]
    file_path = chunks_dir / source_id / f"{chunk_id}.txt"

    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse header and content
        if '# ---' not in content:
            return {'chunk_id': chunk_id, 'text': content}

        header_part, text_part = content.split('# ---', 1)

        # Parse header
        metadata = {'chunk_id': chunk_id}
        for line in header_part.split('\n'):
            line = line.strip()
            if line.startswith('#') and ':' in line:
                key, _, value = line[1:].strip().partition(':')
                metadata[key.strip()] = value.strip()

        metadata['text'] = text_part.strip()
        return metadata

    except (IOError, UnicodeDecodeError):
        return None


def load_chunks_for_source(
    source_id: str,
    chunks_dir: Path
) -> List[Dict[str, Any]]:
    """
    Load all chunks for a source.

    Args:
        source_id: Source UUID
        chunks_dir: Base chunks directory

    Returns:
        List of chunk dictionaries
    """
    source_chunks_dir = chunks_dir / source_id
    if not source_chunks_dir.exists():
        return []

    chunks = []
    for file_path in sorted(source_chunks_dir.glob("*.txt")):
        chunk_id = file_path.stem
        chunk = load_chunk_by_id(chunk_id, chunks_dir)
        if chunk:
            chunks.append(chunk)

    return chunks


def chunks_to_pinecone_format(
    chunks: List[Chunk],
    embeddings: List[List[float]]
) -> List[Dict[str, Any]]:
    """
    Convert chunks and embeddings to Pinecone upsert format.

    Args:
        chunks: List of Chunk objects
        embeddings: List of embedding vectors (same order as chunks)

    Returns:
        List of Pinecone vector dictionaries
    """
    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings must have same length")

    vectors = []
    for chunk, embedding in zip(chunks, embeddings):
        vector = {
            "id": chunk.chunk_id,
            "values": embedding,
            "metadata": {
                "text": chunk.text,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "source_id": chunk.source_id,
                "source_name": chunk.source_name
            }
        }
        vectors.append(vector)

    return vectors


def get_chunks_summary(chunks: List[Chunk]) -> Dict[str, Any]:
    """
    Get summary statistics for a list of chunks.

    Args:
        chunks: List of Chunk objects

    Returns:
        Summary dictionary
    """
    if not chunks:
        return {
            'chunk_count': 0,
            'total_tokens': 0,
            'avg_tokens': 0,
            'pages': []
        }

    total_tokens = sum(count_tokens(c.text) for c in chunks)
    pages = sorted(set(c.page_number for c in chunks))

    return {
        'chunk_count': len(chunks),
        'total_tokens': total_tokens,
        'avg_tokens': total_tokens // len(chunks) if chunks else 0,
        'pages': pages
    }


def delete_chunks_for_source(
    source_id: str,
    chunks_dir: Path
) -> int:
    """
    Delete all chunk files for a specific source.

    Educational Note: When a source is deleted, we delete the entire
    source folder containing all its chunk files.

    Args:
        source_id: The source UUID
        chunks_dir: Base chunks directory

    Returns:
        Number of files deleted
    """
    import shutil

    source_chunks_dir = chunks_dir / source_id
    if not source_chunks_dir.exists():
        return 0

    # Count files before deletion
    deleted_count = len(list(source_chunks_dir.glob("*.txt")))

    # Delete entire source folder
    try:
        shutil.rmtree(source_chunks_dir)
    except Exception as e:
        print(f"Error deleting chunks folder {source_chunks_dir}: {e}")
        return 0

    return deleted_count


# Backward compatibility alias
parse_extracted_text = parse_processed_text

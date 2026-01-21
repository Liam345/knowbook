"""
Embedding utilities for KnowBook.

Provides token counting and embedding decision logic.
Uses tiktoken for fast local token counting (~5% margin vs Claude).
"""
from typing import Tuple, Optional

# Chunking configuration
CHUNK_TOKEN_TARGET = 200  # Target tokens per chunk
CHUNK_MARGIN_PERCENT = 20  # Acceptable margin (±20%)
CHUNK_MIN_TOKENS = int(CHUNK_TOKEN_TARGET * (1 - CHUNK_MARGIN_PERCENT / 100))  # 160
CHUNK_MAX_TOKENS = int(CHUNK_TOKEN_TARGET * (1 + CHUNK_MARGIN_PERCENT / 100))  # 240

# Lazy-loaded tiktoken encoder
_encoder = None


def _get_encoder():
    """
    Get or create the tiktoken encoder.

    Uses cl100k_base which is closest to Claude's tokenizer.
    Lazy-loaded to avoid import overhead.
    """
    global _encoder
    if _encoder is None:
        try:
            import tiktoken
            _encoder = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            _encoder = None
    return _encoder


def count_tokens(text: str) -> int:
    """
    Count tokens in text using tiktoken (fast, local).

    This is the primary method for token counting during chunking operations.
    Uses tiktoken which is ~10,000x faster than API calls.
    Accuracy is ~95% vs Claude (acceptable for chunking decisions).

    Args:
        text: Text to count tokens for

    Returns:
        Token count (or estimate if tiktoken unavailable)
    """
    if not text:
        return 0

    encoder = _get_encoder()
    if encoder:
        return len(encoder.encode(text))

    # Fallback: estimate ~4 characters per token
    return len(text) // 4


def count_tokens_api(text: str, api_key: Optional[str] = None) -> Optional[int]:
    """
    Count tokens using Claude's API (accurate but slow).

    Use this only when exact token counts are needed (billing, quotas).
    For chunking operations, use count_tokens() instead.

    Args:
        text: Text to count tokens for
        api_key: Anthropic API key (uses env var if not provided)

    Returns:
        Exact token count or None on failure
    """
    if not text:
        return 0

    try:
        import anthropic
        import os

        client = anthropic.Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))

        # Use the count_tokens API
        result = client.messages.count_tokens(
            model="claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": text}]
        )
        return result.input_tokens

    except Exception:
        # Fall back to local counting
        return count_tokens(text)


def needs_embedding(text: str) -> Tuple[bool, int, str]:
    """
    Determine if text needs embedding (chunking + vectorization).

    Args:
        text: Processed text content

    Returns:
        Tuple of (should_embed, token_count, reason)
    """
    if not text:
        return False, 0, "No content to embed"

    token_count = count_tokens(text)

    if token_count == 0:
        return False, 0, "No tokens found"

    # Always embed (current strategy)
    if token_count <= CHUNK_MAX_TOKENS:
        return True, token_count, f"{token_count} tokens - single chunk"
    else:
        estimated_chunks = max(1, token_count // CHUNK_TOKEN_TARGET)
        return True, token_count, f"{token_count} tokens - ~{estimated_chunks} chunks"


def estimate_chunks(text: str) -> int:
    """
    Estimate the number of chunks that will be created.

    Args:
        text: Text to estimate chunks for

    Returns:
        Estimated chunk count
    """
    token_count = count_tokens(text)
    if token_count <= CHUNK_MAX_TOKENS:
        return 1
    return max(1, token_count // CHUNK_TOKEN_TARGET)


def format_token_count(count: int) -> str:
    """
    Format token count for display.

    Args:
        count: Token count

    Returns:
        Formatted string (e.g., "200k+" for large counts)
    """
    if count >= 200000:
        return "200k+"
    elif count >= 1000:
        return f"{count // 1000}k"
    else:
        return str(count)

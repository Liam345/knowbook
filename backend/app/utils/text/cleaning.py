"""
Text cleaning utilities for KnowBook.

Provides different levels of text normalization:
1. clean_text_for_embedding - Aggressive cleaning for vector embeddings
2. clean_chunk_text - Removes metadata headers from chunk files
3. normalize_whitespace - Preserves paragraph structure for display
"""
import re
from typing import Optional


def clean_text_for_embedding(text: str) -> str:
    """
    Aggressively clean text for embedding preparation.

    Removes excessive whitespace that adds noise to embeddings while
    preserving semantic content.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text with normalized whitespace
    """
    if not text:
        return ""

    # Strip leading/trailing whitespace
    text = text.strip()

    # Replace 2+ newlines with single newline
    text = re.sub(r'\n{2,}', '\n', text)

    # Replace 2+ spaces with single space
    text = re.sub(r' {2,}', ' ', text)

    # Replace tabs with single space
    text = re.sub(r'\t+', ' ', text)

    # Final trim
    return text.strip()


def clean_chunk_text(text: str) -> str:
    """
    Clean chunk text by removing metadata headers.

    Chunk files have a metadata header followed by "# ---" separator.
    This function extracts just the content after the separator.

    Args:
        text: Chunk file content with potential metadata header

    Returns:
        Cleaned text content without metadata
    """
    if not text:
        return ""

    # Check for metadata separator
    if '# ---' not in text:
        # No metadata header, just clean the text
        return clean_text_for_embedding(text)

    # Split on separator and take the content part
    parts = text.split('# ---', 1)
    if len(parts) < 2:
        return clean_text_for_embedding(text)

    content = parts[1]
    return clean_text_for_embedding(content)


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace while preserving paragraph structure.

    This is less aggressive than clean_text_for_embedding and is
    suitable for display purposes where paragraph breaks matter.

    Args:
        text: Text to normalize

    Returns:
        Text with normalized whitespace but preserved paragraphs
    """
    if not text:
        return ""

    # Strip leading/trailing whitespace
    text = text.strip()

    # Replace 3+ newlines with double newline (preserve paragraphs)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Replace 2+ spaces with single space
    text = re.sub(r' {2,}', ' ', text)

    # Replace tabs with single space
    text = re.sub(r'\t+', ' ', text)

    return text.strip()


def remove_special_characters(text: str, keep_punctuation: bool = True) -> str:
    """
    Remove special characters from text.

    Args:
        text: Text to clean
        keep_punctuation: Whether to keep basic punctuation

    Returns:
        Text with special characters removed
    """
    if not text:
        return ""

    if keep_punctuation:
        # Keep alphanumeric, spaces, and basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text)
    else:
        # Keep only alphanumeric and spaces
        text = re.sub(r'[^\w\s]', '', text)

    return normalize_whitespace(text)

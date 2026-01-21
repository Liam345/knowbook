"""
Page marker utilities for KnowBook.

Provides standardized page boundary markers used across all source types.
Format: === {SOURCE_TYPE} PAGE {N} of {TOTAL} ===

Supported source types:
- PDF, TEXT, DOCX, PPTX, IMAGE, AUDIO, LINK, YOUTUBE, RESEARCH, CSV
"""
import re
from typing import List, Tuple, Optional

# Supported source types for page markers
SUPPORTED_TYPES = [
    'PDF', 'TEXT', 'DOCX', 'PPTX', 'IMAGE',
    'AUDIO', 'LINK', 'YOUTUBE', 'RESEARCH', 'CSV'
]

# Regex pattern to match any page marker
PAGE_MARKER_PATTERN = re.compile(
    r'===\s*(' + '|'.join(SUPPORTED_TYPES) + r')\s+PAGE\s+(\d+)\s+of\s+(\d+)\s*===',
    re.IGNORECASE
)

# Type-specific patterns (for when you need to match a specific type)
TYPE_PATTERNS = {
    source_type: re.compile(
        rf'===\s*{source_type}\s+PAGE\s+(\d+)\s+of\s+(\d+)\s*===',
        re.IGNORECASE
    )
    for source_type in SUPPORTED_TYPES
}


def build_page_marker(source_type: str, page_number: int, total_pages: int) -> str:
    """
    Build a standardized page marker string.

    Args:
        source_type: Type of source (PDF, TEXT, DOCX, etc.)
        page_number: Current page number (1-indexed)
        total_pages: Total number of pages

    Returns:
        Formatted page marker string
    """
    source_type = source_type.upper()
    if source_type not in SUPPORTED_TYPES:
        source_type = 'TEXT'  # Default fallback

    return f"=== {source_type} PAGE {page_number} of {total_pages} ==="


def find_all_markers(text: str) -> List[Tuple[str, int, int, int, int]]:
    """
    Find all page markers in text.

    Args:
        text: Text content to search

    Returns:
        List of tuples: (source_type, page_number, total_pages, start_pos, end_pos)
    """
    if not text:
        return []

    markers = []
    for match in PAGE_MARKER_PATTERN.finditer(text):
        source_type = match.group(1).upper()
        page_number = int(match.group(2))
        total_pages = int(match.group(3))
        start_pos = match.start()
        end_pos = match.end()
        markers.append((source_type, page_number, total_pages, start_pos, end_pos))

    return markers


def get_page_number(marker: str) -> Optional[int]:
    """
    Extract page number from a marker string.

    Args:
        marker: Page marker string

    Returns:
        Page number or None if invalid
    """
    match = PAGE_MARKER_PATTERN.match(marker)
    if match:
        return int(match.group(2))
    return None


def get_total_pages(marker: str) -> Optional[int]:
    """
    Extract total pages from a marker string.

    Args:
        marker: Page marker string

    Returns:
        Total pages or None if invalid
    """
    match = PAGE_MARKER_PATTERN.match(marker)
    if match:
        return int(match.group(3))
    return None


def get_source_type(marker: str) -> Optional[str]:
    """
    Extract source type from a marker string.

    Args:
        marker: Page marker string

    Returns:
        Source type or None if invalid
    """
    match = PAGE_MARKER_PATTERN.match(marker)
    if match:
        return match.group(1).upper()
    return None


def extract_pages(text: str) -> List[Tuple[int, str]]:
    """
    Extract page content between markers.

    Args:
        text: Full processed text with page markers

    Returns:
        List of tuples: (page_number, page_content)
    """
    if not text:
        return []

    markers = find_all_markers(text)
    if not markers:
        # No markers found, treat entire text as page 1
        return [(1, text.strip())]

    pages = []
    for i, (source_type, page_num, total, start, end) in enumerate(markers):
        # Get content from after this marker to before next marker (or end)
        content_start = end
        if i + 1 < len(markers):
            content_end = markers[i + 1][3]  # Start of next marker
        else:
            content_end = len(text)

        content = text[content_start:content_end].strip()
        pages.append((page_num, content))

    return pages


def is_valid_marker(text: str) -> bool:
    """
    Check if a string is a valid page marker.

    Args:
        text: String to check

    Returns:
        True if valid page marker
    """
    return bool(PAGE_MARKER_PATTERN.match(text.strip()))

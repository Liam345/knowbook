"""
Processed output utilities for KnowBook.

Provides standardized output format for all processed sources.
All sources produce a .txt file with consistent header and page markers.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.utils.text.page_markers import build_page_marker


def build_processed_output(
    pages: List[str],
    source_type: str,
    source_name: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build standardized processed output text.

    All processed source files follow this format:
    - Header with metadata
    - "# ---" separator
    - Page markers with content

    Args:
        pages: List of page content strings
        source_type: Type of source (PDF, TEXT, DOCX, etc.)
        source_name: Original filename
        metadata: Additional metadata to include in header

    Returns:
        Formatted processed output string
    """
    source_type = source_type.upper()
    total_pages = len(pages) if pages else 1
    metadata = metadata or {}

    # Build header lines
    header_lines = [
        f"# Extracted from {source_type.lower()} document: {source_name}",
        f"# Type: {source_type}",
        f"# Total pages: {total_pages}",
        f"# Processed at: {datetime.utcnow().isoformat()}",
    ]

    # Add metadata fields (ensure consistent key order)
    standard_keys = ['model_used', 'character_count', 'token_count']
    for key in standard_keys:
        value = metadata.get(key, '')
        header_lines.append(f"# {key}: {value}")

    # Add any additional metadata
    for key, value in metadata.items():
        if key not in standard_keys:
            header_lines.append(f"# {key}: {value}")

    # Add separator
    header_lines.append("# ---")

    # Build content with page markers
    content_parts = []
    for i, page_content in enumerate(pages, start=1):
        marker = build_page_marker(source_type, i, total_pages)
        content_parts.append(f"\n{marker}\n\n{page_content}")

    # Combine header and content
    header = '\n'.join(header_lines)
    content = ''.join(content_parts)

    return header + content


def save_processed_text(
    project_id: str,
    source_id: str,
    content: str,
    data_dir: Optional[Path] = None
) -> Path:
    """
    Save processed text to the processed directory.

    Args:
        project_id: Project UUID
        source_id: Source UUID
        content: Processed text content
        data_dir: Base data directory (defaults to standard location)

    Returns:
        Path to the saved file
    """
    if data_dir is None:
        data_dir = Path(__file__).parent.parent.parent.parent / 'data'

    processed_dir = data_dir / 'projects' / project_id / 'sources' / 'processed'
    processed_dir.mkdir(parents=True, exist_ok=True)

    file_path = processed_dir / f"{source_id}.txt"

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return file_path


def build_and_save_processed_output(
    project_id: str,
    source_id: str,
    pages: List[str],
    source_type: str,
    source_name: str,
    metadata: Optional[Dict[str, Any]] = None,
    data_dir: Optional[Path] = None
) -> Path:
    """
    Build and save processed output in one step.

    Args:
        project_id: Project UUID
        source_id: Source UUID
        pages: List of page content strings
        source_type: Type of source (PDF, TEXT, DOCX, etc.)
        source_name: Original filename
        metadata: Additional metadata to include
        data_dir: Base data directory

    Returns:
        Path to the saved file
    """
    content = build_processed_output(pages, source_type, source_name, metadata)
    return save_processed_text(project_id, source_id, content, data_dir)


def load_processed_text(
    project_id: str,
    source_id: str,
    data_dir: Optional[Path] = None
) -> Optional[str]:
    """
    Load processed text for a source.

    Args:
        project_id: Project UUID
        source_id: Source UUID
        data_dir: Base data directory

    Returns:
        Processed text content or None if not found
    """
    if data_dir is None:
        data_dir = Path(__file__).parent.parent.parent.parent / 'data'

    file_path = data_dir / 'projects' / project_id / 'sources' / 'processed' / f"{source_id}.txt"

    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (IOError, UnicodeDecodeError):
        return None


def parse_processed_header(content: str) -> Dict[str, str]:
    """
    Parse the header section of processed output.

    Args:
        content: Full processed text content

    Returns:
        Dictionary of header key-value pairs
    """
    if not content:
        return {}

    header = {}

    # Find the separator
    if '# ---' not in content:
        return header

    header_section = content.split('# ---')[0]

    for line in header_section.split('\n'):
        line = line.strip()
        if line.startswith('#') and ':' in line:
            # Remove leading '# ' and split on first ':'
            line = line[1:].strip()
            key, _, value = line.partition(':')
            header[key.strip()] = value.strip()

    return header

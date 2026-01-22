"""
Citation utilities for KnowBook.

Handles parsing and formatting of citations in AI responses.
Citation format: [[cite:CHUNK_ID]]
Chunk ID format: {source_id}_page_{N}_chunk_{M}
"""
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


# Regex pattern for citations
CITATION_PATTERN = re.compile(r'\[\[cite:([^\]]+)\]\]')

# Regex pattern for parsing chunk_id
CHUNK_ID_PATTERN = re.compile(r'^(.+)_page_(\d+)_chunk_(\d+)$')


def extract_citations_from_text(text: str) -> List[str]:
    """
    Extract all chunk_ids from citation markers in text.

    Args:
        text: Text containing [[cite:chunk_id]] markers

    Returns:
        List of unique chunk_ids in order of first appearance
    """
    if not text:
        return []

    matches = CITATION_PATTERN.findall(text)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for chunk_id in matches:
        if chunk_id not in seen:
            seen.add(chunk_id)
            unique.append(chunk_id)

    return unique


def parse_chunk_id(chunk_id: str) -> Optional[Dict[str, Any]]:
    """
    Parse a chunk_id into its components.

    Args:
        chunk_id: Format: {source_id}_page_{N}_chunk_{M}

    Returns:
        Dictionary with source_id, page_number, chunk_index or None
    """
    if not chunk_id:
        return None

    match = CHUNK_ID_PATTERN.match(chunk_id)
    if not match:
        return None

    return {
        'source_id': match.group(1),
        'page_number': int(match.group(2)),
        'chunk_index': int(match.group(3))
    }


def get_chunk_content(
    project_id: str,
    chunk_id: str,
    data_dir: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """
    Get chunk content for citation hover display.

    Args:
        project_id: Project UUID
        chunk_id: Chunk identifier
        data_dir: Base data directory

    Returns:
        Dictionary with content, chunk_id, source info or None
    """
    if data_dir is None:
        data_dir = Path(__file__).parent.parent / 'data'

    # Parse chunk_id to get source_id
    parsed = parse_chunk_id(chunk_id)
    if not parsed:
        return None

    source_id = parsed['source_id']

    # Load chunk file
    chunk_file = data_dir / 'projects' / project_id / 'sources' / 'chunks' / source_id / f"{chunk_id}.txt"

    if not chunk_file.exists():
        return None

    try:
        with open(chunk_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse header and content
        metadata = {
            'chunk_id': chunk_id,
            'source_id': source_id,
            'page_number': parsed['page_number'],
            'chunk_index': parsed['chunk_index']
        }

        if '# ---' in content:
            header_part, text_part = content.split('# ---', 1)

            # Parse header for source_name
            for line in header_part.split('\n'):
                line = line.strip()
                if line.startswith('# source_name:'):
                    metadata['source_name'] = line.split(':', 1)[1].strip()

            metadata['content'] = text_part.strip()
        else:
            metadata['content'] = content

        # Get source name from index if not in chunk
        if 'source_name' not in metadata:
            source_name = _get_source_name(project_id, source_id, data_dir)
            if source_name:
                metadata['source_name'] = source_name

        return metadata

    except (IOError, UnicodeDecodeError):
        return None


def _get_source_name(
    project_id: str,
    source_id: str,
    data_dir: Path
) -> Optional[str]:
    """Get source name from sources index."""
    import json

    index_path = data_dir / 'projects' / project_id / 'sources' / 'sources_index.json'
    if not index_path.exists():
        return None

    try:
        with open(index_path, 'r') as f:
            sources = json.load(f)
            for source in sources:
                if source.get('id') == source_id:
                    return source.get('name')
    except (json.JSONDecodeError, IOError):
        pass

    return None


def convert_citations_to_numbered(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Convert [[cite:chunk_id]] markers to numbered references [1], [2], etc.

    Args:
        text: Text with [[cite:chunk_id]] markers

    Returns:
        Tuple of (converted text, mapping of chunk_id to citation number)
    """
    if not text:
        return text, {}

    # Find all unique citations
    chunk_ids = extract_citations_from_text(text)

    # Create mapping
    mapping = {chunk_id: i + 1 for i, chunk_id in enumerate(chunk_ids)}

    # Replace citations with numbered references
    def replace_citation(match):
        chunk_id = match.group(1)
        number = mapping.get(chunk_id, '?')
        # Format as markdown link for hover support
        return f"[{number}](#cite-{chunk_id})"

    converted = CITATION_PATTERN.sub(replace_citation, text)

    return converted, mapping


def get_citation_summary(
    project_id: str,
    chunk_ids: List[str],
    data_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Get summary information for multiple citations.

    Args:
        project_id: Project UUID
        chunk_ids: List of chunk identifiers
        data_dir: Base data directory

    Returns:
        List of citation summaries with source names and pages
    """
    summaries = []

    for chunk_id in chunk_ids:
        chunk_data = get_chunk_content(project_id, chunk_id, data_dir)
        if chunk_data:
            summaries.append({
                'chunk_id': chunk_id,
                'source_name': chunk_data.get('source_name', 'Unknown'),
                'page_number': chunk_data.get('page_number', 1),
                'preview': chunk_data.get('content', '')[:100] + '...'
            })

    return summaries

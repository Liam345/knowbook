"""
Text processor for KnowBook.

Handles plain text files (.txt, .md).
Simplest processor - no extraction needed, just format and embed.
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from app.utils.text import (
    build_and_save_processed_output,
    count_tokens
)
from app.services.embedding_service import embedding_service
from app.services.summary_service import summary_service


def process_text(
    project_id: str,
    source_id: str,
    source: Dict[str, Any],
    raw_file_path: Path,
    source_service
) -> Dict[str, Any]:
    """
    Process a plain text file.

    Pipeline:
    1. Read raw text file
    2. Create processed output with page markers
    3. Generate embeddings
    4. Generate summary

    Args:
        project_id: Project UUID
        source_id: Source UUID
        source: Source metadata dictionary
        raw_file_path: Path to the raw text file
        source_service: Source service for status updates

    Returns:
        Result dictionary with success status and info
    """
    try:
        # Read raw text file
        with open(raw_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            return {
                "success": False,
                "error": "File is empty"
            }

        # Count tokens and characters
        token_count = count_tokens(content)
        character_count = len(content)

        # Build and save processed output
        source_name = source.get('name', source.get('original_name', 'unknown'))
        metadata = {
            'character_count': character_count,
            'token_count': token_count
        }

        data_dir = Path(__file__).parent.parent.parent / 'data'
        build_and_save_processed_output(
            project_id=project_id,
            source_id=source_id,
            pages=[content],  # Single page for text files
            source_type='TEXT',
            source_name=source_name,
            metadata=metadata,
            data_dir=data_dir
        )

        processing_info = {
            'character_count': character_count,
            'token_count': token_count,
            'pages_processed': 1,
            'processed_at': datetime.utcnow().isoformat()
        }

        # Update status to embedding
        source_service._update_source_status(
            project_id, source_id, 'embedding',
            processing_info=processing_info
        )

        # Process embeddings
        embedding_info = embedding_service.process_embeddings(
            project_id=project_id,
            source_id=source_id,
            source_name=source_name
        )

        # Generate summary
        summary_info = summary_service.generate_summary(
            project_id=project_id,
            source_id=source_id,
            source_name=source_name
        )

        return {
            "success": True,
            "processing_info": processing_info,
            "embedding_info": embedding_info,
            "summary_info": summary_info
        }

    except UnicodeDecodeError:
        return {
            "success": False,
            "error": "File encoding not supported (try UTF-8)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

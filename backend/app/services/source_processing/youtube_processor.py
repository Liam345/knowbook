"""
YouTube processor for KnowBook.

Handles YouTube video transcripts.
Uses youtube-transcript-api for fast transcript extraction.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from app.utils.text import (
    build_and_save_processed_output,
    count_tokens
)
from app.services.integrations.youtube import youtube_service
from app.services.embedding_service import embedding_service
from app.services.summary_service import summary_service


def process_youtube(
    project_id: str,
    source_id: str,
    source: Dict[str, Any],
    raw_file_path: Path,
    source_service
) -> Dict[str, Any]:
    """
    Process a YouTube video transcript.

    Pipeline:
    1. Load URL from .link file
    2. Extract transcript using YouTube API
    3. Create processed output with page markers
    4. Generate embeddings
    5. Generate summary

    Args:
        project_id: Project UUID
        source_id: Source UUID
        source: Source metadata dictionary
        raw_file_path: Path to the .link file containing URL
        source_service: Source service for status updates

    Returns:
        Result dictionary with success status and info
    """
    try:
        # Load URL from .link file
        with open(raw_file_path, 'r', encoding='utf-8') as f:
            link_data = json.load(f)

        url = link_data.get('url', '')
        if not url:
            return {
                "success": False,
                "error": "No URL found in link file"
            }

        # Extract transcript
        result = youtube_service.get_transcript(url, include_timestamps=True)

        if not result.get('success'):
            return {
                "success": False,
                "error": result.get('error', 'Failed to extract transcript')
            }

        transcript = result.get('transcript', '')
        if not transcript:
            return {
                "success": False,
                "error": "No transcript content extracted"
            }

        # Get metadata from result
        video_id = result.get('video_id', '')
        language = result.get('language', 'en')
        is_auto_generated = result.get('is_auto_generated', True)
        duration_seconds = result.get('duration_seconds', 0)
        segment_count = result.get('segment_count', 0)

        # Count tokens and characters
        token_count = count_tokens(transcript)
        character_count = len(transcript)

        # Format duration
        duration_str = _format_duration(duration_seconds)

        # Build and save processed output
        source_name = source.get('name', source.get('original_name', 'YouTube Video'))
        metadata = {
            'url': url,
            'video_id': video_id,
            'language': language,
            'is_auto_generated': str(is_auto_generated).lower(),
            'duration': duration_str,
            'segment_count': segment_count,
            'character_count': character_count,
            'token_count': token_count
        }

        data_dir = Path(__file__).parent.parent.parent / 'data'
        build_and_save_processed_output(
            project_id=project_id,
            source_id=source_id,
            pages=[transcript],  # Single page for YouTube
            source_type='YOUTUBE',
            source_name=source_name,
            metadata=metadata,
            data_dir=data_dir
        )

        # Update link file with fetched data
        link_data['fetched'] = True
        link_data['fetched_at'] = datetime.utcnow().isoformat()
        link_data['video_id'] = video_id
        link_data['language'] = language
        link_data['is_auto_generated'] = is_auto_generated
        link_data['duration_seconds'] = duration_seconds

        with open(raw_file_path, 'w', encoding='utf-8') as f:
            json.dump(link_data, f, indent=2)

        processing_info = {
            'video_id': video_id,
            'language': language,
            'is_auto_generated': is_auto_generated,
            'duration': duration_str,
            'segment_count': segment_count,
            'character_count': character_count,
            'token_count': token_count,
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

    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Invalid link file format"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _format_duration(seconds: float) -> str:
    """
    Format seconds as MM:SS or HH:MM:SS.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

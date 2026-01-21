"""
YouTube service for KnowBook.

Extracts transcripts from YouTube videos using youtube-transcript-api.
Supports both manual and auto-generated captions.
"""
import re
from typing import Dict, Any, Optional, List


# YouTube URL patterns
YOUTUBE_PATTERNS = [
    r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
    r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
    r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
]


class YouTubeService:
    """
    Service for extracting transcripts from YouTube videos.

    Uses youtube-transcript-api to fetch captions without downloading videos.
    Prioritizes manual captions over auto-generated for better quality.
    """

    def __init__(self):
        """Initialize the YouTube service."""
        self._api = None

    def _get_api(self):
        """Get or create the YouTube transcript API."""
        if self._api is None:
            from youtube_transcript_api import YouTubeTranscriptApi
            self._api = YouTubeTranscriptApi

        return self._api

    def is_youtube_url(self, url: str) -> bool:
        """
        Check if a URL is a YouTube video URL.

        Args:
            url: URL to check

        Returns:
            True if YouTube URL
        """
        return self.extract_video_id(url) is not None

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from a YouTube URL.

        Handles multiple URL formats:
        - youtube.com/watch?v=VIDEO_ID
        - youtu.be/VIDEO_ID
        - youtube.com/embed/VIDEO_ID

        Args:
            url: YouTube URL

        Returns:
            Video ID or None if not a valid YouTube URL
        """
        if not url:
            return None

        for pattern in YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def get_transcript(
        self,
        url: str,
        include_timestamps: bool = True,
        preferred_languages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get transcript for a YouTube video.

        Args:
            url: YouTube video URL
            include_timestamps: Whether to include timestamps in output
            preferred_languages: Preferred language codes (default: ['en'])

        Returns:
            Dictionary with transcript info and content
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            return {
                "success": False,
                "error": "Invalid YouTube URL"
            }

        if preferred_languages is None:
            preferred_languages = ['en']

        try:
            api = self._get_api()

            # Fetch transcript
            transcript = api.get_transcript(video_id, languages=preferred_languages)

            # Format transcript text
            formatted_text = self._format_transcript(transcript, include_timestamps)

            # Calculate duration from last segment
            duration_seconds = 0
            if transcript:
                last_segment = transcript[-1]
                duration_seconds = last_segment.get('start', 0) + last_segment.get('duration', 0)

            # Detect if auto-generated (heuristic: check caption metadata)
            is_auto_generated = self._check_if_auto_generated(video_id, preferred_languages)

            return {
                "success": True,
                "video_id": video_id,
                "transcript": formatted_text,
                "language": preferred_languages[0],
                "is_auto_generated": is_auto_generated,
                "duration_seconds": duration_seconds,
                "segment_count": len(transcript)
            }

        except Exception as e:
            error_message = self._parse_error(str(e))
            return {
                "success": False,
                "video_id": video_id,
                "error": error_message
            }

    def _format_transcript(
        self,
        transcript: List[Dict[str, Any]],
        include_timestamps: bool
    ) -> str:
        """
        Format transcript segments into readable text.

        Args:
            transcript: List of transcript segments
            include_timestamps: Whether to include timestamps

        Returns:
            Formatted transcript text
        """
        if not transcript:
            return ""

        lines = []
        for segment in transcript:
            text = segment.get('text', '').strip()
            if not text:
                continue

            if include_timestamps:
                start = segment.get('start', 0)
                timestamp = self._format_timestamp(start)
                lines.append(f"[{timestamp}] {text}")
            else:
                lines.append(text)

        return '\n'.join(lines)

    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds as MM:SS or HH:MM:SS.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in a human-readable way.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string
        """
        return self._format_timestamp(seconds)

    def _check_if_auto_generated(
        self,
        video_id: str,
        languages: List[str]
    ) -> bool:
        """
        Check if transcript is auto-generated.

        Args:
            video_id: YouTube video ID
            languages: Languages to check

        Returns:
            True if likely auto-generated
        """
        try:
            api = self._get_api()
            transcript_list = api.list_transcripts(video_id)

            # Check if manual transcript exists
            for transcript in transcript_list:
                if not transcript.is_generated:
                    return False

            return True

        except Exception:
            # Default to True (assume auto-generated if can't determine)
            return True

    def _parse_error(self, error: str) -> str:
        """
        Parse YouTube API errors into user-friendly messages.

        Args:
            error: Raw error message

        Returns:
            User-friendly error message
        """
        error_lower = error.lower()

        if "disabled" in error_lower:
            return "Transcripts are disabled for this video"

        if "unavailable" in error_lower or "private" in error_lower:
            return "Video is unavailable (private, deleted, or region-locked)"

        if "no transcript" in error_lower:
            return "No transcript available for this video"

        if "could not retrieve" in error_lower:
            return "Could not retrieve transcript for this video"

        return f"Error fetching transcript: {error}"


# Global instance
youtube_service = YouTubeService()

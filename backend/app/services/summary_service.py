"""
Summary service for KnowBook.

Generates concise summaries using Claude Haiku.
Uses smart sampling for large documents (selects representative chunks).
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.utils.text import count_tokens, load_chunks_for_source

# Summary configuration
SUMMARY_MODEL = "claude-haiku-4-5-20251001"
SUMMARY_TARGET_TOKENS = 175  # Target 150-200 tokens
MAX_INPUT_TOKENS = 20000  # Max tokens to send to Haiku
MAX_CHUNKS_TO_SAMPLE = 8  # Sample up to 8 chunks for large docs


class SummaryService:
    """
    Service for generating AI summaries of source content.

    Uses Claude Haiku for cost-effective summary generation.
    Smart sampling for large documents ensures comprehensive coverage.
    """

    def __init__(self):
        """Initialize the summary service."""
        self.data_dir = Path(__file__).parent.parent / 'data'
        self._client = None

    def _get_client(self):
        """Get or create the Anthropic client."""
        if self._client is None:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")

            import anthropic
            self._client = anthropic.Anthropic(api_key=api_key)

        return self._client

    def is_configured(self) -> bool:
        """Check if Anthropic is configured."""
        return bool(os.getenv('ANTHROPIC_API_KEY'))

    def generate_summary(
        self,
        project_id: str,
        source_id: str,
        source_name: str,
        processed_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a summary for a source.

        Strategy:
        - Small sources (< 2500 tokens): Use full content
        - Large sources: Sample up to 8 evenly distributed chunks

        Args:
            project_id: Project UUID
            source_id: Source UUID
            source_name: Display name for source
            processed_text: Optional processed text (used for small sources)

        Returns:
            Dictionary with summary info
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "Anthropic not configured"
            }

        try:
            # Try to get content from chunks first
            chunks_dir = self.data_dir / 'projects' / project_id / 'sources' / 'chunks'
            chunks = load_chunks_for_source(source_id, chunks_dir)

            if chunks:
                # Use sampled chunks for summary
                content = self._get_sampled_content(chunks)
            elif processed_text:
                # Use processed text directly for small sources
                content = processed_text
            else:
                # Load processed text
                processed_path = self.data_dir / 'projects' / project_id / 'sources' / 'processed' / f"{source_id}.txt"
                if not processed_path.exists():
                    return {
                        "success": False,
                        "error": "No content found for summary"
                    }
                with open(processed_path, 'r', encoding='utf-8') as f:
                    content = f.read()

            if not content:
                return {
                    "success": False,
                    "error": "No content found for summary"
                }

            # Generate summary
            summary = self._call_haiku_for_summary(content, source_name)

            if summary:
                return {
                    "success": True,
                    "summary": summary,
                    "model": SUMMARY_MODEL,
                    "generated_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate summary"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _get_sampled_content(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Get sampled content from chunks.

        Selects evenly distributed chunks to capture intro, middle, and conclusion.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Concatenated sampled content
        """
        if not chunks:
            return ""

        # If few chunks, use all
        if len(chunks) <= MAX_CHUNKS_TO_SAMPLE:
            selected_chunks = chunks
        else:
            # Select evenly distributed chunks
            indices = self._get_chunk_indices(len(chunks), MAX_CHUNKS_TO_SAMPLE)
            selected_chunks = [chunks[i] for i in indices]

        # Concatenate chunk texts
        texts = []
        for chunk in selected_chunks:
            text = chunk.get('text', '')
            if text:
                texts.append(text)

        return '\n\n'.join(texts)

    def _get_chunk_indices(self, total_chunks: int, chunks_to_select: int) -> List[int]:
        """
        Get evenly distributed chunk indices.

        Always includes first and last chunk.

        Args:
            total_chunks: Total number of chunks
            chunks_to_select: Number of chunks to select

        Returns:
            List of chunk indices
        """
        if chunks_to_select >= total_chunks:
            return list(range(total_chunks))

        if chunks_to_select == 1:
            return [0]

        if chunks_to_select == 2:
            return [0, total_chunks - 1]

        # Linear interpolation for even distribution
        step = (total_chunks - 1) / (chunks_to_select - 1)
        indices = [round(i * step) for i in range(chunks_to_select)]

        return indices

    def _call_haiku_for_summary(self, content: str, source_name: str) -> Optional[str]:
        """
        Call Claude Haiku to generate a summary.

        Args:
            content: Content to summarize
            source_name: Name of the source

        Returns:
            Generated summary or None
        """
        try:
            client = self._get_client()

            # Truncate content if too long
            token_count = count_tokens(content)
            if token_count > MAX_INPUT_TOKENS:
                # Simple truncation - take first MAX_INPUT_TOKENS worth
                # This is a fallback; normally sampling handles this
                content = content[:MAX_INPUT_TOKENS * 4]  # Rough char estimate

            prompt = f"""Generate a concise summary (150-200 words) of the following content from "{source_name}".

Focus on:
- Main topics and themes
- Key facts and findings
- Important conclusions

Content:
{content}

Summary:"""

            response = client.messages.create(
                model=SUMMARY_MODEL,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            if response.content and len(response.content) > 0:
                return response.content[0].text.strip()

            return None

        except Exception as e:
            print(f"Haiku summary error: {e}")
            return None


# Global instance
summary_service = SummaryService()

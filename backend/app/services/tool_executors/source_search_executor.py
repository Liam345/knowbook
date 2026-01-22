"""
Source Search Executor for KnowBook.

Executes the search_sources tool with hybrid search strategy:
- Small sources (<1000 tokens): Return all chunks
- Large sources: Combine keyword + semantic search

Returns formatted chunks with chunk_ids for citation.
"""
from pathlib import Path
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional

from app.services.integrations.openai import openai_service
from app.services.integrations.pinecone import pinecone_service
from app.utils.text import load_chunks_for_source, count_tokens


class SourceSearchExecutor:
    """
    Executes source search with hybrid search strategy.

    Combines local keyword search (fuzzy matching) with
    semantic search (Pinecone vectors) for best results.
    """

    # Fuzzy matching threshold (0-1, higher = stricter)
    FUZZY_THRESHOLD = 0.7

    # Maximum results per search type
    MAX_RESULTS = 5

    # Token threshold for small source optimization
    SMALL_SOURCE_THRESHOLD = 1000

    def __init__(self):
        """Initialize the source search executor."""
        self.data_dir = Path(__file__).parent.parent.parent / 'data'

    def execute(
        self,
        project_id: str,
        source_id: str,
        keywords: Optional[List[str]] = None,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute source search with hybrid strategy.

        Args:
            project_id: Project UUID
            source_id: Source UUID to search within
            keywords: Optional keywords for text matching
            query: Optional semantic search query

        Returns:
            Dictionary with content (formatted chunks) or error
        """
        try:
            # Load source metadata
            source = self._load_source_metadata(project_id, source_id)
            if not source:
                return {
                    "success": False,
                    "error": f"Source not found: {source_id}"
                }

            # Check source status
            if source.get('status') != 'ready':
                return {
                    "success": False,
                    "error": f"Source not ready (status: {source.get('status')})"
                }

            # Load all chunks for this source
            chunks = self._load_source_chunks(project_id, source_id)
            if not chunks:
                return {
                    "success": False,
                    "error": "No chunks found for source"
                }

            # Check source size - small sources return all chunks
            total_tokens = sum(c.get('token_count', 0) for c in chunks)
            if total_tokens < self.SMALL_SOURCE_THRESHOLD:
                # Small source: return all chunks
                result_chunks = chunks
            else:
                # Large source: use hybrid search
                result_chunks = self._hybrid_search(
                    project_id, source_id, chunks, keywords, query
                )

            if not result_chunks:
                return {
                    "success": True,
                    "content": f"No relevant content found in '{source.get('name')}'."
                }

            # Format chunks for Claude with citation info
            formatted = self._format_chunks(result_chunks, source)

            return {
                "success": True,
                "content": formatted
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _hybrid_search(
        self,
        project_id: str,
        source_id: str,
        chunks: List[Dict[str, Any]],
        keywords: Optional[List[str]],
        query: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining keyword and semantic search.

        Args:
            project_id: Project UUID
            source_id: Source UUID
            chunks: All chunks for the source
            keywords: Optional keywords for text matching
            query: Optional semantic query

        Returns:
            List of matching chunks (deduplicated, sorted by score)
        """
        results = []

        # Keyword search (local, fast)
        if keywords:
            keyword_results = self._keyword_search(chunks, keywords)
            results.extend(keyword_results)

        # Semantic search (Pinecone)
        if query and openai_service.is_configured() and pinecone_service.is_configured():
            semantic_results = self._semantic_search(project_id, source_id, query)
            results.extend(semantic_results)

        # If no keywords or query, return top chunks by position
        if not keywords and not query:
            return chunks[:self.MAX_RESULTS]

        # Deduplicate by chunk_id, keeping highest score
        return self._dedupe_results(results)

    def _keyword_search(
        self,
        chunks: List[Dict[str, Any]],
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Perform local keyword search with fuzzy matching.

        Args:
            chunks: All chunks to search
            keywords: Keywords to match

        Returns:
            List of matching chunks with scores
        """
        scored_chunks = []

        for chunk in chunks:
            text = chunk.get('text', '').lower()
            score = 0.0

            for keyword in keywords:
                keyword_lower = keyword.lower()

                # Exact match (case-insensitive)
                if keyword_lower in text:
                    # Score by frequency
                    score += text.count(keyword_lower) * 2.0
                else:
                    # Fuzzy match via difflib
                    words = text.split()
                    for word in words:
                        # Clean word of punctuation
                        clean_word = ''.join(c for c in word if c.isalnum())
                        if not clean_word:
                            continue

                        similarity = SequenceMatcher(
                            None, keyword_lower, clean_word
                        ).ratio()

                        if similarity >= self.FUZZY_THRESHOLD:
                            score += similarity

            if score > 0:
                scored_chunk = {**chunk, '_search_score': score}
                scored_chunks.append(scored_chunk)

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x.get('_search_score', 0), reverse=True)

        return scored_chunks[:self.MAX_RESULTS]

    def _semantic_search(
        self,
        project_id: str,
        source_id: str,
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search via Pinecone.

        Args:
            project_id: Project UUID (Pinecone namespace)
            source_id: Source UUID for filtering
            query: Search query

        Returns:
            List of matching chunks with scores
        """
        try:
            # Create query embedding
            query_vector = openai_service.create_embedding(query)
            if not query_vector:
                return []

            # Search Pinecone with source filter
            results = pinecone_service.query_vectors(
                query_vector=query_vector,
                namespace=project_id,
                top_k=self.MAX_RESULTS,
                filter_dict={"source_id": {"$eq": source_id}},
                include_metadata=True
            )

            # Convert Pinecone format to chunk format
            chunks = []
            for result in results:
                metadata = result.get('metadata', {})
                chunks.append({
                    'chunk_id': result.get('id'),
                    'text': metadata.get('text', ''),
                    'page_number': metadata.get('page_number', 1),
                    'source_id': metadata.get('source_id', source_id),
                    'source_name': metadata.get('source_name', ''),
                    '_search_score': result.get('score', 0)
                })

            return chunks

        except Exception as e:
            print(f"Semantic search error: {e}")
            return []

    def _dedupe_results(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate results by chunk_id, keeping highest score.

        Args:
            results: List of chunks (possibly with duplicates)

        Returns:
            Deduplicated list sorted by score
        """
        seen = {}

        for chunk in results:
            chunk_id = chunk.get('chunk_id')
            if not chunk_id:
                continue

            score = chunk.get('_search_score', 0)

            if chunk_id not in seen or score > seen[chunk_id].get('_search_score', 0):
                seen[chunk_id] = chunk

        # Sort by score descending
        deduped = list(seen.values())
        deduped.sort(key=lambda x: x.get('_search_score', 0), reverse=True)

        return deduped[:self.MAX_RESULTS]

    def _format_chunks(
        self,
        chunks: List[Dict[str, Any]],
        source: Dict[str, Any]
    ) -> str:
        """
        Format chunks for Claude with citation information.

        Args:
            chunks: List of chunks to format
            source: Source metadata

        Returns:
            Formatted string for Claude
        """
        source_name = source.get('name', 'Unknown Source')

        lines = [
            f"## Content from: {source_name}",
            f"Found {len(chunks)} relevant section(s).",
            "Use the chunk_id in citations: [[cite:chunk_id]]",
            ""
        ]

        for chunk in chunks:
            chunk_id = chunk.get('chunk_id', 'unknown')
            page = chunk.get('page_number', 1)
            text = chunk.get('text', '')

            lines.append(f"**chunk_id:** {chunk_id}")
            lines.append(f"**Page:** {page}")
            lines.append(text)
            lines.append("")  # Blank line between chunks

        return "\n".join(lines)

    def _load_source_metadata(
        self,
        project_id: str,
        source_id: str
    ) -> Optional[Dict[str, Any]]:
        """Load source metadata from index."""
        import json

        index_path = self.data_dir / 'projects' / project_id / 'sources' / 'sources_index.json'
        if not index_path.exists():
            return None

        try:
            with open(index_path, 'r') as f:
                sources = json.load(f)
                return next((s for s in sources if s['id'] == source_id), None)
        except (json.JSONDecodeError, IOError):
            return None

    def _load_source_chunks(
        self,
        project_id: str,
        source_id: str
    ) -> List[Dict[str, Any]]:
        """Load all chunks for a source."""
        chunks_dir = self.data_dir / 'projects' / project_id / 'sources' / 'chunks'
        return load_chunks_for_source(source_id, chunks_dir)


# Global instance
source_search_executor = SourceSearchExecutor()

"""
Embedding service for KnowBook.

Orchestrates the embedding pipeline:
1. Parse processed text into chunks
2. Create embeddings via OpenAI
3. Store vectors in Pinecone
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.utils.text import (
    parse_processed_text,
    save_chunks_to_files,
    chunks_to_pinecone_format,
    needs_embedding,
    count_tokens,
    load_processed_text
)
from app.services.integrations.openai import openai_service
from app.services.integrations.pinecone import pinecone_service


class EmbeddingService:
    """
    Service for managing the embedding pipeline.

    Handles:
    - Parsing processed text into chunks
    - Saving chunk files
    - Creating embeddings via OpenAI
    - Storing vectors in Pinecone
    """

    def __init__(self):
        """Initialize the embedding service."""
        self.data_dir = Path(__file__).parent.parent / 'data'

    def process_embeddings(
        self,
        project_id: str,
        source_id: str,
        source_name: str,
        processed_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process embeddings for a source.

        Full pipeline: parse → chunk → embed → store

        Args:
            project_id: Project UUID
            source_id: Source UUID
            source_name: Display name for source
            processed_text: Processed text content (loads from file if not provided)

        Returns:
            Dictionary with embedding info
        """
        # Load processed text if not provided
        if processed_text is None:
            processed_text = load_processed_text(project_id, source_id, self.data_dir)

        if not processed_text:
            return {
                "success": False,
                "is_embedded": False,
                "error": "No processed text found",
                "embedded_at": None
            }

        # Check if embedding is needed
        should_embed, token_count, reason = needs_embedding(processed_text)
        if not should_embed:
            return {
                "success": True,
                "is_embedded": False,
                "token_count": token_count,
                "reason": reason,
                "embedded_at": None
            }

        # Check if services are configured
        if not openai_service.is_configured():
            return {
                "success": False,
                "is_embedded": False,
                "error": "OpenAI not configured",
                "token_count": token_count,
                "embedded_at": None
            }

        if not pinecone_service.is_configured():
            return {
                "success": False,
                "is_embedded": False,
                "error": "Pinecone not configured",
                "token_count": token_count,
                "embedded_at": None
            }

        try:
            # Parse into chunks
            chunks = parse_processed_text(processed_text, source_id, source_name)
            if not chunks:
                return {
                    "success": True,
                    "is_embedded": False,
                    "token_count": token_count,
                    "reason": "No chunks created",
                    "embedded_at": None
                }

            # Save chunk files
            chunks_dir = self.data_dir / 'projects' / project_id / 'sources' / 'chunks'
            save_chunks_to_files(chunks, chunks_dir)

            # Create embeddings
            chunk_texts = [c.text for c in chunks]
            embeddings = openai_service.create_embeddings_batch(chunk_texts)

            if embeddings is None:
                return {
                    "success": False,
                    "is_embedded": False,
                    "error": "Failed to create embeddings",
                    "token_count": token_count,
                    "chunk_count": len(chunks),
                    "embedded_at": None
                }

            # Format for Pinecone
            vectors = chunks_to_pinecone_format(chunks, embeddings)

            # Upsert to Pinecone
            result = pinecone_service.upsert_vectors(vectors, namespace=project_id)

            if "error" in result:
                return {
                    "success": False,
                    "is_embedded": False,
                    "error": result["error"],
                    "token_count": token_count,
                    "chunk_count": len(chunks),
                    "embedded_at": None
                }

            return {
                "success": True,
                "is_embedded": True,
                "token_count": token_count,
                "chunk_count": len(chunks),
                "vector_count": result.get("upserted_count", len(vectors)),
                "embedding_model": "text-embedding-3-small",
                "reason": reason,
                "embedded_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "is_embedded": False,
                "error": str(e),
                "embedded_at": None
            }

    def delete_embeddings(
        self,
        project_id: str,
        source_id: str
    ) -> bool:
        """
        Delete embeddings for a source.

        Args:
            project_id: Project UUID
            source_id: Source UUID

        Returns:
            True if successful
        """
        try:
            # Delete from Pinecone
            pinecone_service.delete_by_source(source_id, namespace=project_id)

            # Delete chunk files
            chunks_dir = self.data_dir / 'projects' / project_id / 'sources' / 'chunks' / source_id
            if chunks_dir.exists():
                import shutil
                shutil.rmtree(chunks_dir)

            return True

        except Exception as e:
            print(f"Error deleting embeddings: {e}")
            return False

    def search_similar(
        self,
        project_id: str,
        query: str,
        top_k: int = 10,
        source_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using semantic search.

        Args:
            project_id: Project UUID
            query: Search query
            top_k: Number of results
            source_filter: Optional list of source_ids to filter by

        Returns:
            List of match results
        """
        if not openai_service.is_configured():
            return []

        try:
            # Create query embedding
            query_embedding = openai_service.create_embedding(query)
            if not query_embedding:
                return []

            # Build filter
            filter_dict = None
            if source_filter:
                filter_dict = {"source_id": {"$in": source_filter}}

            # Query Pinecone
            results = pinecone_service.query_vectors(
                query_vector=query_embedding,
                namespace=project_id,
                top_k=top_k,
                filter_dict=filter_dict,
                include_metadata=True
            )

            return results

        except Exception as e:
            print(f"Error searching embeddings: {e}")
            return []


# Global instance
embedding_service = EmbeddingService()

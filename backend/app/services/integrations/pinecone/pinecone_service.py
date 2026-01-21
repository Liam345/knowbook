"""
Pinecone service for KnowBook.

Provides vector storage and retrieval using Pinecone.
Uses project_id as namespace for source isolation.
"""
import os
from typing import List, Dict, Any, Optional

# Pinecone configuration
DEFAULT_TOP_K = 10  # Default number of results
EMBEDDING_DIMENSIONS = 1536  # Must match OpenAI embedding dimensions


class PineconeService:
    """
    Service for Pinecone vector database operations.

    Uses lazy initialization and project-based namespaces.
    Each project has its own namespace for complete isolation.
    """

    def __init__(self):
        """Initialize the Pinecone service."""
        self._index = None
        self._initialized = False

    def _get_index(self):
        """
        Get or create the Pinecone index connection.

        Raises:
            ValueError: If Pinecone is not configured
        """
        if self._index is None:
            api_key = os.getenv('PINECONE_API_KEY')
            index_name = os.getenv('PINECONE_INDEX_NAME', 'knowbook')

            if not api_key:
                raise ValueError("PINECONE_API_KEY not found in environment")

            from pinecone import Pinecone
            pc = Pinecone(api_key=api_key)

            # Connect to existing index
            self._index = pc.Index(index_name)
            self._initialized = True

        return self._index

    def is_configured(self) -> bool:
        """Check if Pinecone is configured."""
        return bool(os.getenv('PINECONE_API_KEY'))

    def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]],
        namespace: str
    ) -> Dict[str, Any]:
        """
        Upsert vectors to Pinecone.

        Args:
            vectors: List of vector dictionaries with id, values, metadata
            namespace: Namespace (typically project_id)

        Returns:
            Result dictionary with upsert count
        """
        if not vectors:
            return {"upserted_count": 0}

        try:
            index = self._get_index()

            # Pinecone expects list of tuples or dicts
            # Format: [(id, values, metadata), ...]
            formatted_vectors = []
            for v in vectors:
                formatted_vectors.append({
                    "id": v["id"],
                    "values": v["values"],
                    "metadata": v.get("metadata", {})
                })

            # Upsert in batches of 100
            batch_size = 100
            total_upserted = 0

            for i in range(0, len(formatted_vectors), batch_size):
                batch = formatted_vectors[i:i + batch_size]
                result = index.upsert(vectors=batch, namespace=namespace)
                total_upserted += result.upserted_count

            return {"upserted_count": total_upserted}

        except Exception as e:
            print(f"Pinecone upsert error: {e}")
            return {"error": str(e), "upserted_count": 0}

    def query_vectors(
        self,
        query_vector: List[float],
        namespace: str,
        top_k: int = DEFAULT_TOP_K,
        filter_dict: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query vectors from Pinecone.

        Args:
            query_vector: Query embedding vector
            namespace: Namespace to search (typically project_id)
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            include_metadata: Whether to include metadata in results

        Returns:
            List of match dictionaries with id, score, metadata
        """
        try:
            index = self._get_index()

            result = index.query(
                vector=query_vector,
                namespace=namespace,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=include_metadata
            )

            matches = []
            for match in result.matches:
                matches.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata if include_metadata else {}
                })

            return matches

        except Exception as e:
            print(f"Pinecone query error: {e}")
            return []

    def delete_vectors(
        self,
        ids: List[str],
        namespace: str
    ) -> bool:
        """
        Delete vectors by ID.

        Args:
            ids: List of vector IDs to delete
            namespace: Namespace containing vectors

        Returns:
            True if successful
        """
        if not ids:
            return True

        try:
            index = self._get_index()
            index.delete(ids=ids, namespace=namespace)
            return True

        except Exception as e:
            print(f"Pinecone delete error: {e}")
            return False

    def delete_by_source(
        self,
        source_id: str,
        namespace: str
    ) -> bool:
        """
        Delete all vectors for a source.

        Args:
            source_id: Source UUID
            namespace: Project namespace

        Returns:
            True if successful
        """
        try:
            index = self._get_index()

            # Delete by metadata filter
            index.delete(
                filter={"source_id": {"$eq": source_id}},
                namespace=namespace
            )
            return True

        except Exception as e:
            print(f"Pinecone delete by source error: {e}")
            return False

    def delete_namespace(self, namespace: str) -> bool:
        """
        Delete all vectors in a namespace.

        Args:
            namespace: Namespace to delete

        Returns:
            True if successful
        """
        try:
            index = self._get_index()
            index.delete(delete_all=True, namespace=namespace)
            return True

        except Exception as e:
            print(f"Pinecone delete namespace error: {e}")
            return False

    def get_namespace_stats(self, namespace: str) -> Dict[str, Any]:
        """
        Get statistics for a namespace.

        Args:
            namespace: Namespace to check

        Returns:
            Stats dictionary
        """
        try:
            index = self._get_index()
            stats = index.describe_index_stats()

            ns_stats = stats.namespaces.get(namespace, {})
            return {
                "vector_count": getattr(ns_stats, 'vector_count', 0),
                "namespace": namespace
            }

        except Exception as e:
            print(f"Pinecone stats error: {e}")
            return {"vector_count": 0, "namespace": namespace, "error": str(e)}


# Global instance
pinecone_service = PineconeService()

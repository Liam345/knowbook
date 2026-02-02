"""
Pinecone Service - Vector database operations for semantic search.

Educational Note: Pinecone is a managed vector database that enables:
- Storing high-dimensional vectors (embeddings)
- Fast similarity search using cosine/dot product metrics
- Metadata filtering for hybrid search

Our application uses:
- Index: "growthxlearn" (created automatically on API key validation)
- Dimensions: 1536 (OpenAI text-embedding-3-small)
- Metric: cosine similarity
- Namespace: project_id (isolate vectors by project)
"""
import os
from typing import List, Dict, Any, Optional
from pinecone import Pinecone


class PineconeService:
    """
    Service for Pinecone vector database operations.

    Educational Note: This service handles:
    - Upserting vectors (insert/update)
    - Semantic search (query by vector)
    - Deleting vectors (by ID or filter)
    - Namespace management (one namespace per project)
    """

    # Index configuration (must match validation_service.py)
    INDEX_NAME = "growthxlearn"

    def __init__(self):
        """Initialize the Pinecone service."""
        self._client: Optional[Pinecone] = None
        self._index = None

    def _get_client(self) -> Pinecone:
        """
        Get or create the Pinecone client.

        Educational Note: Lazy initialization ensures we don't fail
        at import time if the API key isn't set yet.

        Raises:
            ValueError: If PINECONE_API_KEY is not set
        """
        if self._client is None:
            api_key = os.getenv('PINECONE_API_KEY')
            if not api_key:
                raise ValueError("PINECONE_API_KEY not found in environment")
            self._client = Pinecone(api_key=api_key)
        return self._client

    def _get_index(self):
        """
        Get the Pinecone index.

        Educational Note: The index must exist before we can use it.
        It's created automatically when the user validates their API key
        in AppSettings (via validation_service.validate_pinecone_key).

        Raises:
            ValueError: If the index doesn't exist
        """
        if self._index is None:
            client = self._get_client()

            if not client.has_index(self.INDEX_NAME):
                raise ValueError(
                    f"Pinecone index '{self.INDEX_NAME}' not found. "
                    "Please validate your Pinecone API key in App Settings first."
                )

            self._index = client.Index(self.INDEX_NAME)

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
        top_k: int = 5,
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

    def search(
        self,
        query_vector: List[float],
        namespace: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using a query vector.

        Educational Note: This is the core of RAG retrieval:
        1. User query is converted to embedding (done elsewhere)
        2. Query vector is compared to all vectors in namespace
        3. Most similar vectors (by cosine similarity) are returned
        4. Metadata (including original text) is retrieved

        Args:
            query_vector: The embedding of the search query
            namespace: Project ID to search within
            top_k: Number of results to return
            filter: Optional metadata filter (e.g., {"source_id": "abc"})
            include_metadata: Whether to return metadata with results

        Returns:
            List of search results with format:
            [
                {
                    "id": "chunk_id",
                    "score": 0.95,  # Similarity score
                    "metadata": {"text": "...", "page": 1, ...}
                },
                ...
            ]
        """
        index = self._get_index()

        response = index.query(
            vector=query_vector,
            namespace=namespace,
            top_k=top_k,
            filter=filter,
            include_metadata=include_metadata
        )

        # Convert to simple dict format
        results = []
        for match in response.matches:
            result = {
                "id": match.id,
                "score": match.score,
            }
            if include_metadata and match.metadata:
                result["metadata"] = dict(match.metadata)
            results.append(result)

        return results

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

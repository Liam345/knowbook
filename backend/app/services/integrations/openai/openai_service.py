"""
OpenAI service for KnowBook.

Provides embedding generation using OpenAI's text-embedding-3-small model.
"""
import os
from typing import List, Optional, Dict, Any

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536  # Default dimensions for text-embedding-3-small
MAX_BATCH_SIZE = 100  # OpenAI's recommended batch size


class OpenAIService:
    """
    Service for OpenAI API operations.

    Primarily used for generating embeddings for vector search.
    Uses lazy initialization to avoid errors if API key not configured.
    """

    def __init__(self):
        """Initialize the OpenAI service."""
        self._client = None

    def _get_client(self):
        """
        Get or create the OpenAI client.

        Raises:
            ValueError: If OPENAI_API_KEY is not configured
        """
        if self._client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")

            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)

        return self._client

    def is_configured(self) -> bool:
        """Check if OpenAI is configured."""
        return bool(os.getenv('OPENAI_API_KEY'))

    def create_embedding(self, text: str) -> Optional[List[float]]:
        """
        Create an embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None on failure
        """
        if not text:
            return None

        try:
            client = self._get_client()
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding

        except Exception as e:
            print(f"OpenAI embedding error: {e}")
            return None

    def create_embeddings_batch(
        self,
        texts: List[str]
    ) -> Optional[List[List[float]]]:
        """
        Create embeddings for multiple texts in batch.

        More efficient than calling create_embedding multiple times.
        Automatically handles batching for large lists.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (same order as input) or None on failure
        """
        if not texts:
            return []

        try:
            client = self._get_client()
            all_embeddings = []

            # Process in batches
            for i in range(0, len(texts), MAX_BATCH_SIZE):
                batch = texts[i:i + MAX_BATCH_SIZE]

                response = client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=batch
                )

                # Extract embeddings in order
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

            return all_embeddings

        except Exception as e:
            print(f"OpenAI batch embedding error: {e}")
            return None

    def get_embedding_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding configuration.

        Returns:
            Dictionary with model info
        """
        return {
            "model": EMBEDDING_MODEL,
            "dimensions": EMBEDDING_DIMENSIONS,
            "max_batch_size": MAX_BATCH_SIZE,
            "configured": self.is_configured()
        }


# Global instance
openai_service = OpenAIService()

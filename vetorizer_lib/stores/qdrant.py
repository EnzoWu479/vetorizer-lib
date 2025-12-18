"""Qdrant vector store implementation.

This module provides the QdrantStore class for storing and searching
embeddings in a Qdrant vector database.
"""

import hashlib
from typing import Any
from uuid import UUID, uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from vetorizer_lib.exceptions import ConnectionError, SearchError
from vetorizer_lib.models.config import DistanceMetric
from vetorizer_lib.models.document import Document, SearchResult


class QdrantStore:
    """Vector store using Qdrant database.

    Supports in-memory, file-based, and remote Qdrant instances.

    Args:
        url: Qdrant server URL. If None, uses local storage.
        api_key: API key for Qdrant Cloud.
        path: Local path for file-based storage.
        collection_name: Name of the collection.
        distance_metric: Similarity metric (cosine, euclidean, dot).
        vector_size: Dimension of vectors. Auto-detected on first upsert if None.

    Example:
        >>> store = QdrantStore(collection_name="products")
        >>> store.upsert([document])
        >>> results = store.search(query_vector, limit=5)
    """

    DISTANCE_MAP = {
        DistanceMetric.COSINE: Distance.COSINE,
        DistanceMetric.EUCLIDEAN: Distance.EUCLID,
        DistanceMetric.DOT: Distance.DOT,
    }

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        path: str | None = None,
        collection_name: str = "default",
        distance_metric: DistanceMetric = DistanceMetric.COSINE,
        vector_size: int | None = None,
    ) -> None:
        """Initialize the Qdrant store."""
        self._collection_name = collection_name
        self._distance_metric = distance_metric
        self._vector_size = vector_size
        self._collection_initialized = False

        try:
            if url:
                self._client = QdrantClient(url=url, api_key=api_key)
            elif path:
                self._client = QdrantClient(path=path)
            else:
                # In-memory mode
                self._client = QdrantClient(":memory:")
        except Exception as e:
            raise ConnectionError(
                f"Cannot connect to Qdrant. URL: {url}, Path: {path}",
                cause=e,
            ) from e

    def _ensure_collection(self, vector_size: int) -> None:
        """Ensure the collection exists with correct configuration.

        Args:
            vector_size: Dimension of vectors to store.
        """
        if self._collection_initialized:
            return

        collections = self._client.get_collections().collections
        exists = any(c.name == self._collection_name for c in collections)

        if not exists:
            distance = self.DISTANCE_MAP.get(self._distance_metric, Distance.COSINE)
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )

        self._vector_size = vector_size
        self._collection_initialized = True

    def _to_uuid(self, doc_id: str) -> str:
        """Convert a string ID to a valid UUID string.

        Uses MD5 hash to generate a deterministic UUID from any string.

        Args:
            doc_id: Original document ID.

        Returns:
            UUID string representation.
        """
        # Try to parse as UUID first
        try:
            UUID(doc_id)
            return doc_id
        except ValueError:
            pass

        # Generate deterministic UUID from string using MD5
        hash_bytes = hashlib.md5(doc_id.encode()).digest()
        return str(UUID(bytes=hash_bytes))

    def upsert(self, documents: list[Document]) -> None:
        """Insert or update documents in the vector store.

        Args:
            documents: List of documents with embeddings to store.

        Raises:
            ConnectionError: If the vector store is unreachable.
        """
        if not documents:
            return

        # Get vector size from first document
        vector_size = len(documents[0].embedding)
        self._ensure_collection(vector_size)

        points = [
            PointStruct(
                id=self._to_uuid(doc.id) if doc.id else str(uuid4()),
                vector=doc.embedding,
                payload={
                    "content": doc.content,
                    "content_type": doc.content_type.value,
                    "original_id": doc.id,  # Store original ID for retrieval
                    **doc.metadata,
                },
            )
            for doc in documents
        ]

        try:
            self._client.upsert(
                collection_name=self._collection_name,
                points=points,
            )
        except Exception as e:
            raise ConnectionError(
                f"Failed to upsert documents to collection '{self._collection_name}'",
                cause=e,
            ) from e

    def search(
        self,
        vector: list[float],
        limit: int = 10,
        min_score: float | None = None,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors.

        Args:
            vector: Query vector to search for.
            limit: Maximum number of results to return.
            min_score: Minimum similarity score threshold.
            filter: Metadata filter conditions (not yet implemented).

        Returns:
            List of SearchResult objects sorted by similarity.

        Raises:
            SearchError: If the search fails.
        """
        # Check if collection exists
        collections = self._client.get_collections().collections
        exists = any(c.name == self._collection_name for c in collections)

        if not exists:
            return []

        try:
            results = self._client.query_points(
                collection_name=self._collection_name,
                query=vector,
                limit=limit,
                score_threshold=min_score,
            ).points
        except Exception as e:
            raise SearchError(
                f"Search failed in collection '{self._collection_name}'",
                cause=e,
            ) from e

        return [
            SearchResult(
                id=hit.payload.get("original_id", str(hit.id)) if hit.payload else str(hit.id),
                score=hit.score,
                content=hit.payload.get("content", "") if hit.payload else "",
                metadata={
                    k: v
                    for k, v in (hit.payload or {}).items()
                    if k not in ("content", "content_type", "original_id")
                },
            )
            for hit in results
        ]

    def delete(self, ids: list[str]) -> None:
        """Delete documents by ID.

        Args:
            ids: List of document IDs to delete.

        Raises:
            ConnectionError: If the vector store is unreachable.
        """
        if not ids:
            return

        # Convert IDs to UUIDs
        uuid_ids = [self._to_uuid(doc_id) for doc_id in ids]

        try:
            self._client.delete(
                collection_name=self._collection_name,
                points_selector=uuid_ids,
            )
        except Exception as e:
            raise ConnectionError(
                f"Failed to delete documents from collection '{self._collection_name}'",
                cause=e,
            ) from e

    def count(self) -> int:
        """Return the number of documents in the collection.

        Returns:
            Number of documents stored.

        Raises:
            ConnectionError: If the vector store is unreachable.
        """
        collections = self._client.get_collections().collections
        exists = any(c.name == self._collection_name for c in collections)

        if not exists:
            return 0

        try:
            info = self._client.get_collection(self._collection_name)
            return info.points_count
        except Exception as e:
            raise ConnectionError(
                f"Failed to get count from collection '{self._collection_name}'",
                cause=e,
            ) from e

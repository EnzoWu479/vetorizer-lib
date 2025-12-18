"""Base protocol for vector stores.

This module defines the VectorStore protocol that all store implementations must follow.
"""

from typing import Any, Protocol

from vetorizer_lib.models.document import Document, SearchResult


class VectorStore(Protocol):
    """Protocol for vector database operations.

    All vector store implementations must provide these methods.
    This enables dependency injection and easy mocking for tests.

    Example:
        >>> class MockStore:
        ...     def upsert(self, documents: list[Document]) -> None:
        ...         pass
        ...     def search(
        ...         self,
        ...         vector: list[float],
        ...         limit: int = 10,
        ...         min_score: float | None = None,
        ...         filter: dict[str, Any] | None = None
        ...     ) -> list[SearchResult]:
        ...         return []
        ...     def delete(self, ids: list[str]) -> None:
        ...         pass
        ...     def count(self) -> int:
        ...         return 0
        ...
        >>> store: VectorStore = MockStore()
    """

    def upsert(self, documents: list[Document]) -> None:
        """Insert or update documents in the vector store.

        Args:
            documents: List of documents with embeddings to store.

        Raises:
            ConnectionError: If the vector store is unreachable.
        """
        ...

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
            filter: Metadata filter conditions.

        Returns:
            List of SearchResult objects sorted by similarity.

        Raises:
            SearchError: If the search fails.
        """
        ...

    def delete(self, ids: list[str]) -> None:
        """Delete documents by ID.

        Args:
            ids: List of document IDs to delete.

        Raises:
            ConnectionError: If the vector store is unreachable.
        """
        ...

    def count(self) -> int:
        """Return the number of documents in the collection.

        Returns:
            Number of documents stored.

        Raises:
            ConnectionError: If the vector store is unreachable.
        """
        ...

"""Integration tests for Qdrant vector store.

Tests for QdrantStore with real Qdrant (in-memory mode).
"""

import pytest

from vetorizer_lib.models.document import ContentType, Document, SearchResult


class TestQdrantStoreUpsert:
    """Tests for QdrantStore.upsert method."""

    def test_upsert_single_document(self) -> None:
        """QdrantStore can upsert a single document."""
        from vetorizer_lib.stores.qdrant import QdrantStore

        store = QdrantStore(collection_name="test_upsert_single")
        
        doc = Document(
            id="doc-001",
            content="Test content",
            content_type=ContentType.TEXT,
            embedding=[0.1] * 384,
            metadata={"title": "Test"},
        )
        
        store.upsert([doc])
        assert store.count() == 1

    def test_upsert_multiple_documents(self) -> None:
        """QdrantStore can upsert multiple documents."""
        from vetorizer_lib.stores.qdrant import QdrantStore

        store = QdrantStore(collection_name="test_upsert_multi")
        
        docs = [
            Document(
                id=f"doc-{i}",
                content=f"Content {i}",
                embedding=[0.1 * i] * 384,
            )
            for i in range(5)
        ]
        
        store.upsert(docs)
        assert store.count() == 5

    def test_upsert_updates_existing_document(self) -> None:
        """QdrantStore updates document with same ID."""
        from vetorizer_lib.stores.qdrant import QdrantStore

        store = QdrantStore(collection_name="test_upsert_update")
        
        doc1 = Document(
            id="doc-001",
            content="Original content",
            embedding=[0.1] * 384,
        )
        store.upsert([doc1])
        
        doc2 = Document(
            id="doc-001",
            content="Updated content",
            embedding=[0.2] * 384,
        )
        store.upsert([doc2])
        
        assert store.count() == 1

    def test_upsert_preserves_metadata(self) -> None:
        """QdrantStore preserves document metadata."""
        from vetorizer_lib.stores.qdrant import QdrantStore

        store = QdrantStore(collection_name="test_upsert_meta")
        
        doc = Document(
            id="doc-001",
            content="Test content",
            embedding=[0.1] * 384,
            metadata={"category": "test", "price": 99.99},
        )
        
        store.upsert([doc])
        
        # Search to retrieve and verify metadata
        results = store.search([0.1] * 384, limit=1)
        assert len(results) == 1
        assert results[0].metadata["category"] == "test"
        assert results[0].metadata["price"] == 99.99


class TestQdrantStoreSearch:
    """Tests for QdrantStore.search method."""

    def test_search_returns_results(self) -> None:
        """QdrantStore.search returns SearchResult objects."""
        from vetorizer_lib.stores.qdrant import QdrantStore

        store = QdrantStore(collection_name="test_search_results")
        
        docs = [
            Document(id="doc-1", content="First", embedding=[1.0, 0.0, 0.0] + [0.0] * 381),
            Document(id="doc-2", content="Second", embedding=[0.0, 1.0, 0.0] + [0.0] * 381),
        ]
        store.upsert(docs)
        
        results = store.search([1.0, 0.0, 0.0] + [0.0] * 381, limit=2)
        
        assert len(results) == 2
        assert isinstance(results[0], SearchResult)
        assert results[0].id == "doc-1"  # Most similar

    def test_search_respects_limit(self) -> None:
        """QdrantStore.search respects limit parameter."""
        from vetorizer_lib.stores.qdrant import QdrantStore

        store = QdrantStore(collection_name="test_search_limit")
        
        docs = [
            Document(id=f"doc-{i}", content=f"Content {i}", embedding=[0.1] * 384)
            for i in range(10)
        ]
        store.upsert(docs)
        
        results = store.search([0.1] * 384, limit=3)
        assert len(results) == 3

    def test_search_returns_scores(self) -> None:
        """QdrantStore.search returns similarity scores."""
        from vetorizer_lib.stores.qdrant import QdrantStore

        store = QdrantStore(collection_name="test_search_scores")
        
        doc = Document(id="doc-1", content="Test", embedding=[0.1] * 384)
        store.upsert([doc])
        
        results = store.search([0.1] * 384, limit=1)
        
        assert len(results) == 1
        # Allow small floating point tolerance above 1.0
        assert 0.0 <= results[0].score <= 1.01

    def test_search_empty_collection(self) -> None:
        """QdrantStore.search on empty collection returns empty list."""
        from vetorizer_lib.stores.qdrant import QdrantStore

        store = QdrantStore(collection_name="test_search_empty")
        
        results = store.search([0.1] * 384, limit=10)
        assert results == []


class TestQdrantStoreDelete:
    """Tests for QdrantStore.delete method."""

    def test_delete_removes_document(self) -> None:
        """QdrantStore.delete removes document by ID."""
        from vetorizer_lib.stores.qdrant import QdrantStore

        store = QdrantStore(collection_name="test_delete")
        
        doc = Document(id="doc-001", content="Test", embedding=[0.1] * 384)
        store.upsert([doc])
        assert store.count() == 1
        
        store.delete(["doc-001"])
        assert store.count() == 0

    def test_delete_multiple_documents(self) -> None:
        """QdrantStore.delete removes multiple documents."""
        from vetorizer_lib.stores.qdrant import QdrantStore

        store = QdrantStore(collection_name="test_delete_multi")
        
        docs = [
            Document(id=f"doc-{i}", content=f"Content {i}", embedding=[0.1] * 384)
            for i in range(5)
        ]
        store.upsert(docs)
        
        store.delete(["doc-0", "doc-2", "doc-4"])
        assert store.count() == 2

"""Unit tests for vetorizer_lib models.

Tests for all dataclasses and enums in the models module.
"""

import pytest

from vetorizer_lib.models.config import (
    DistanceMetric,
    IngestConfig,
    Modality,
    VectorStoreConfig,
)
from vetorizer_lib.models.document import (
    ContentType,
    Document,
    IngestResult,
    SearchResult,
)


class TestContentType:
    """Tests for ContentType enum."""

    def test_text_value(self) -> None:
        """ContentType.TEXT should have value 'text'."""
        assert ContentType.TEXT.value == "text"

    def test_image_value(self) -> None:
        """ContentType.IMAGE should have value 'image'."""
        assert ContentType.IMAGE.value == "image"

    def test_is_string_enum(self) -> None:
        """ContentType should be usable as a string."""
        assert str(ContentType.TEXT) == "ContentType.TEXT"
        assert ContentType.TEXT == "text"


class TestModality:
    """Tests for Modality enum."""

    def test_text_value(self) -> None:
        """Modality.TEXT should have value 'text'."""
        assert Modality.TEXT.value == "text"

    def test_image_value(self) -> None:
        """Modality.IMAGE should have value 'image'."""
        assert Modality.IMAGE.value == "image"

    def test_multimodal_value(self) -> None:
        """Modality.MULTIMODAL should have value 'multimodal'."""
        assert Modality.MULTIMODAL.value == "multimodal"


class TestDistanceMetric:
    """Tests for DistanceMetric enum."""

    def test_cosine_value(self) -> None:
        """DistanceMetric.COSINE should have value 'cosine'."""
        assert DistanceMetric.COSINE.value == "cosine"

    def test_euclidean_value(self) -> None:
        """DistanceMetric.EUCLIDEAN should have value 'euclidean'."""
        assert DistanceMetric.EUCLIDEAN.value == "euclidean"

    def test_dot_value(self) -> None:
        """DistanceMetric.DOT should have value 'dot'."""
        assert DistanceMetric.DOT.value == "dot"


class TestDocument:
    """Tests for Document dataclass."""

    def test_create_minimal_document(self) -> None:
        """Document can be created with minimal required fields."""
        doc = Document(id="doc-001", content="Hello world")
        assert doc.id == "doc-001"
        assert doc.content == "Hello world"
        assert doc.content_type == ContentType.TEXT
        assert doc.embedding == []
        assert doc.metadata == {}

    def test_create_full_document(self) -> None:
        """Document can be created with all fields."""
        doc = Document(
            id="doc-002",
            content="Test content",
            content_type=ContentType.IMAGE,
            embedding=[0.1, 0.2, 0.3],
            metadata={"title": "Test"},
        )
        assert doc.id == "doc-002"
        assert doc.content_type == ContentType.IMAGE
        assert doc.embedding == [0.1, 0.2, 0.3]
        assert doc.metadata == {"title": "Test"}

    def test_document_metadata_is_mutable(self) -> None:
        """Document metadata can be modified after creation."""
        doc = Document(id="doc-003", content="Test")
        doc.metadata["key"] = "value"
        assert doc.metadata["key"] == "value"


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_create_search_result(self) -> None:
        """SearchResult can be created with required fields."""
        result = SearchResult(
            id="doc-001",
            score=0.95,
            content="Matching content",
        )
        assert result.id == "doc-001"
        assert result.score == 0.95
        assert result.content == "Matching content"
        assert result.metadata == {}

    def test_search_result_with_metadata(self) -> None:
        """SearchResult can include metadata."""
        result = SearchResult(
            id="doc-002",
            score=0.85,
            content="Another match",
            metadata={"category": "test"},
        )
        assert result.metadata == {"category": "test"}

    def test_score_range(self) -> None:
        """SearchResult score can be any float (validation is external)."""
        result = SearchResult(id="doc", score=1.5, content="test")
        assert result.score == 1.5


class TestIngestResult:
    """Tests for IngestResult dataclass."""

    def test_create_ingest_result(self) -> None:
        """IngestResult can be created with required fields."""
        result = IngestResult(
            processed=100,
            skipped=5,
            failed=2,
        )
        assert result.processed == 100
        assert result.skipped == 5
        assert result.failed == 2
        assert result.errors == []
        assert result.duration_seconds == 0.0

    def test_ingest_result_with_errors(self) -> None:
        """IngestResult can include error messages."""
        result = IngestResult(
            processed=98,
            skipped=0,
            failed=2,
            errors=["Row 5: empty content", "Row 10: invalid data"],
            duration_seconds=12.5,
        )
        assert len(result.errors) == 2
        assert result.duration_seconds == 12.5


class TestVectorStoreConfig:
    """Tests for VectorStoreConfig dataclass."""

    def test_default_config(self) -> None:
        """VectorStoreConfig has sensible defaults."""
        config = VectorStoreConfig()
        assert config.url is None
        assert config.api_key is None
        assert config.collection_name == "default"
        assert config.distance_metric == DistanceMetric.COSINE
        assert config.path is None

    def test_remote_config(self) -> None:
        """VectorStoreConfig can be configured for remote Qdrant."""
        config = VectorStoreConfig(
            url="http://localhost:6333",
            collection_name="products",
        )
        assert config.url == "http://localhost:6333"
        assert config.collection_name == "products"

    def test_cloud_config(self) -> None:
        """VectorStoreConfig can be configured for Qdrant Cloud."""
        config = VectorStoreConfig(
            url="https://xyz.cloud.qdrant.io",
            api_key="secret-key",
            collection_name="my-collection",
        )
        assert config.api_key == "secret-key"


class TestIngestConfig:
    """Tests for IngestConfig dataclass."""

    def test_minimal_config(self) -> None:
        """IngestConfig can be created with minimal required fields."""
        config = IngestConfig(
            file_path="data.csv",
            content_column="description",
        )
        assert config.file_path == "data.csv"
        assert config.content_column == "description"
        assert config.id_column is None
        assert config.metadata_columns == []
        assert config.batch_size == 100
        assert config.skip_empty is True

    def test_full_config(self) -> None:
        """IngestConfig can be created with all fields."""
        config = IngestConfig(
            file_path="products.csv",
            content_column="description",
            id_column="product_id",
            metadata_columns=["title", "category", "price"],
            batch_size=50,
            skip_empty=False,
        )
        assert config.id_column == "product_id"
        assert len(config.metadata_columns) == 3
        assert config.batch_size == 50
        assert config.skip_empty is False

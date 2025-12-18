"""Contract tests for vetorizer_lib public API.

Tests to ensure the public API contract remains stable.
"""

import pytest
from pathlib import Path


class TestVetorizerClientContract:
    """Contract tests for VetorizerClient."""

    def test_client_can_be_instantiated_with_defaults(self) -> None:
        """VetorizerClient can be created with no arguments."""
        from vetorizer_lib import VetorizerClient

        client = VetorizerClient()
        assert client is not None

    def test_client_accepts_model_name(self) -> None:
        """VetorizerClient accepts model_name parameter."""
        from vetorizer_lib import VetorizerClient

        client = VetorizerClient(model_name="sentence-transformers/all-MiniLM-L6-v2")
        assert client is not None

    def test_client_accepts_qdrant_url(self) -> None:
        """VetorizerClient accepts qdrant_url parameter."""
        from vetorizer_lib import VetorizerClient

        client = VetorizerClient(qdrant_url="http://localhost:6333")
        assert client is not None

    def test_client_accepts_collection_name(self) -> None:
        """VetorizerClient accepts collection_name parameter."""
        from vetorizer_lib import VetorizerClient

        client = VetorizerClient(collection_name="my_collection")
        assert client is not None

    def test_client_has_ingest_csv_method(self) -> None:
        """VetorizerClient has ingest_csv method."""
        from vetorizer_lib import VetorizerClient

        client = VetorizerClient()
        assert hasattr(client, "ingest_csv")
        assert callable(client.ingest_csv)

    def test_client_has_search_method(self) -> None:
        """VetorizerClient has search method."""
        from vetorizer_lib import VetorizerClient

        client = VetorizerClient()
        assert hasattr(client, "search")
        assert callable(client.search)

    def test_client_has_ingest_images_method(self) -> None:
        """VetorizerClient has ingest_images method."""
        from vetorizer_lib import VetorizerClient

        client = VetorizerClient()
        assert hasattr(client, "ingest_images")
        assert callable(client.ingest_images)

    def test_client_has_search_by_image_method(self) -> None:
        """VetorizerClient has search_by_image method."""
        from vetorizer_lib import VetorizerClient

        client = VetorizerClient()
        assert hasattr(client, "search_by_image")
        assert callable(client.search_by_image)


class TestIngestResultContract:
    """Contract tests for IngestResult dataclass."""

    def test_ingest_result_has_processed_field(self) -> None:
        """IngestResult has processed field."""
        from vetorizer_lib import IngestResult

        result = IngestResult(processed=10, skipped=0, failed=0)
        assert hasattr(result, "processed")
        assert result.processed == 10

    def test_ingest_result_has_skipped_field(self) -> None:
        """IngestResult has skipped field."""
        from vetorizer_lib import IngestResult

        result = IngestResult(processed=10, skipped=5, failed=0)
        assert hasattr(result, "skipped")
        assert result.skipped == 5

    def test_ingest_result_has_failed_field(self) -> None:
        """IngestResult has failed field."""
        from vetorizer_lib import IngestResult

        result = IngestResult(processed=10, skipped=0, failed=2)
        assert hasattr(result, "failed")
        assert result.failed == 2

    def test_ingest_result_has_errors_field(self) -> None:
        """IngestResult has errors field."""
        from vetorizer_lib import IngestResult

        result = IngestResult(processed=10, skipped=0, failed=0, errors=["error1"])
        assert hasattr(result, "errors")
        assert "error1" in result.errors

    def test_ingest_result_has_duration_field(self) -> None:
        """IngestResult has duration_seconds field."""
        from vetorizer_lib import IngestResult

        result = IngestResult(processed=10, skipped=0, failed=0, duration_seconds=5.5)
        assert hasattr(result, "duration_seconds")
        assert result.duration_seconds == 5.5


class TestSearchResultContract:
    """Contract tests for SearchResult dataclass."""

    def test_search_result_has_id_field(self) -> None:
        """SearchResult has id field."""
        from vetorizer_lib import SearchResult

        result = SearchResult(id="doc-1", score=0.9, content="test")
        assert hasattr(result, "id")
        assert result.id == "doc-1"

    def test_search_result_has_score_field(self) -> None:
        """SearchResult has score field."""
        from vetorizer_lib import SearchResult

        result = SearchResult(id="doc-1", score=0.95, content="test")
        assert hasattr(result, "score")
        assert result.score == 0.95

    def test_search_result_has_content_field(self) -> None:
        """SearchResult has content field."""
        from vetorizer_lib import SearchResult

        result = SearchResult(id="doc-1", score=0.9, content="test content")
        assert hasattr(result, "content")
        assert result.content == "test content"

    def test_search_result_has_metadata_field(self) -> None:
        """SearchResult has metadata field."""
        from vetorizer_lib import SearchResult

        result = SearchResult(id="doc-1", score=0.9, content="test", metadata={"key": "val"})
        assert hasattr(result, "metadata")
        assert result.metadata["key"] == "val"


class TestSearchContract:
    """Contract tests for search functionality (US2)."""

    def test_search_returns_list(self) -> None:
        """VetorizerClient.search returns a list."""
        from vetorizer_lib import VetorizerClient

        # Just verify the method signature - actual search tested in integration
        client = VetorizerClient()
        assert callable(client.search)

    def test_search_accepts_limit_parameter(self) -> None:
        """VetorizerClient.search accepts limit parameter."""
        from vetorizer_lib import VetorizerClient
        import inspect

        sig = inspect.signature(VetorizerClient.search)
        assert "limit" in sig.parameters

    def test_search_accepts_min_score_parameter(self) -> None:
        """VetorizerClient.search accepts min_score parameter."""
        from vetorizer_lib import VetorizerClient
        import inspect

        sig = inspect.signature(VetorizerClient.search)
        assert "min_score" in sig.parameters

    def test_search_accepts_filter_parameter(self) -> None:
        """VetorizerClient.search accepts filter parameter."""
        from vetorizer_lib import VetorizerClient
        import inspect

        sig = inspect.signature(VetorizerClient.search)
        assert "filter" in sig.parameters


class TestExceptionsContract:
    """Contract tests for exception classes."""

    def test_vetorizer_error_exists(self) -> None:
        """VetorizerError exception exists."""
        from vetorizer_lib import VetorizerError

        assert issubclass(VetorizerError, Exception)

    def test_configuration_error_exists(self) -> None:
        """ConfigurationError exception exists."""
        from vetorizer_lib import ConfigurationError, VetorizerError

        assert issubclass(ConfigurationError, VetorizerError)

    def test_connection_error_exists(self) -> None:
        """ConnectionError exception exists."""
        from vetorizer_lib import ConnectionError, VetorizerError

        assert issubclass(ConnectionError, VetorizerError)

    def test_model_load_error_exists(self) -> None:
        """ModelLoadError exception exists."""
        from vetorizer_lib import ModelLoadError, VetorizerError

        assert issubclass(ModelLoadError, VetorizerError)

    def test_ingest_error_exists(self) -> None:
        """IngestError exception exists."""
        from vetorizer_lib import IngestError, VetorizerError

        assert issubclass(IngestError, VetorizerError)

    def test_search_error_exists(self) -> None:
        """SearchError exception exists."""
        from vetorizer_lib import SearchError, VetorizerError

        assert issubclass(SearchError, VetorizerError)

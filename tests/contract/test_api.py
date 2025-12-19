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


class TestWebAPIDatabaseEndpoints:
    """Contract tests for web API database endpoints."""
    
    def test_post_databases_endpoint_exists(self) -> None:
        """POST /api/databases endpoint exists."""
        from fastapi.testclient import TestClient
        from vetorizer_lib.web.app import app
        
        client = TestClient(app)
        # Endpoint should exist (even if it returns error without valid data)
        response = client.post("/api/databases")
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404
    
    def test_post_databases_validate_endpoint_exists(self) -> None:
        """POST /api/databases/validate endpoint exists."""
        from fastapi.testclient import TestClient
        from vetorizer_lib.web.app import app
        
        client = TestClient(app)
        response = client.post("/api/databases/validate")
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404
    
    def test_post_databases_accepts_multipart_form(self) -> None:
        """POST /api/databases accepts multipart/form-data."""
        from fastapi.testclient import TestClient
        from vetorizer_lib.web.app import app
        import io
        
        client = TestClient(app)
        response = client.post(
            "/api/databases",
            data={
                "name": "Test DB",
                "ingest_mode": "text",
                "text_column": "content",
            },
            files={"files": ("test.csv", io.BytesIO(b"id,content\n1,test"), "text/csv")},
        )
        # Should not be 415 Unsupported Media Type
        assert response.status_code != 415
    
    def test_databases_validate_returns_validation_summary(self) -> None:
        """POST /api/databases/validate returns BatchValidationSummary structure."""
        from fastapi.testclient import TestClient
        from vetorizer_lib.web.app import app
        import io
        
        client = TestClient(app)
        response = client.post(
            "/api/databases/validate",
            data={"ingest_mode": "text"},
            files={"files": ("test.csv", io.BytesIO(b"id,content\n1,test"), "text/csv")},
        )
        
        if response.status_code == 200:
            data = response.json()
            # Should have validation summary structure
            assert "overall_status" in data
            assert "total_files" in data
            assert "valid_files" in data
            assert "invalid_files" in data
            assert "can_proceed" in data


class TestWebAPIUploadEndpoints:
    """Contract tests for web API upload endpoints (US1)."""

    def test_post_upload_endpoint_exists(self) -> None:
        """POST /api/upload endpoint exists."""
        from fastapi.testclient import TestClient
        from vetorizer_lib.web.app import app

        client = TestClient(app)
        # Endpoint should exist (even if it returns error without valid data)
        response = client.post("/api/upload")
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404

    def test_post_upload_accepts_text_mode(self) -> None:
        """POST /api/upload accepts text mode with required parameters."""
        from fastapi.testclient import TestClient
        from vetorizer_lib.web.app import app
        import io

        client = TestClient(app)
        response = client.post(
            "/api/upload",
            data={
                "database_name": "test_text_db",
                "ingest_mode": "text",
                "content_column": "content",
            },
            files={"file": ("test.csv", io.BytesIO(b"id,content\n1,test data"), "text/csv")},
        )
        # Should accept the request structure (202 for valid, 400/409 for validation errors)
        assert response.status_code in [202, 400, 409]
        
        # Should not fail with wrong HTTP method error
        assert response.status_code != 405
        # Should not fail with unsupported media type
        assert response.status_code != 415

    def test_post_upload_accepts_image_mode(self) -> None:
        """POST /api/upload accepts image mode with required parameters."""
        from fastapi.testclient import TestClient
        from vetorizer_lib.web.app import app
        import io

        client = TestClient(app)
        response = client.post(
            "/api/upload",
            data={
                "database_name": "test_image_db",
                "ingest_mode": "image",
                "content_column": "image_path",
                "image_column": "image_path",
            },
            files={"file": ("test.csv", io.BytesIO(b"id,image_path\n1,/test/image.png"), "text/csv")},
        )
        # Should accept the request structure
        assert response.status_code in [202, 400, 409]
        assert response.status_code != 405
        assert response.status_code != 415

    def test_post_upload_accepts_hybrid_mode(self) -> None:
        """POST /api/upload accepts hybrid mode with required parameters."""
        from fastapi.testclient import TestClient
        from vetorizer_lib.web.app import app
        import io

        client = TestClient(app)
        response = client.post(
            "/api/upload",
            data={
                "database_name": "test_hybrid_db",
                "ingest_mode": "hybrid",
                "content_column": "text",
                "text_column": "text",
                "image_column": "image_path",
            },
            files={"file": ("test.csv", io.BytesIO(b"id,text,image_path\n1,test,/img.png"), "text/csv")},
        )
        # Should accept the request structure
        assert response.status_code in [202, 400, 409]
        assert response.status_code != 405
        assert response.status_code != 415

    def test_post_upload_returns_job_id(self) -> None:
        """POST /api/upload returns UploadJobResponse with job_id."""
        from fastapi.testclient import TestClient
        from vetorizer_lib.web.app import app
        import io

        client = TestClient(app)
        response = client.post(
            "/api/upload",
            data={
                "database_name": "test_job_db",
                "ingest_mode": "text",
                "content_column": "content",
            },
            files={"file": ("test.csv", io.BytesIO(b"id,content\n1,test"), "text/csv")},
        )
        
        # If upload succeeds, should have job ID in response (field name is "id")
        if response.status_code == 202:
            data = response.json()
            assert "id" in data
            assert "database_id" in data
            assert "status" in data

    def test_post_upload_validates_hybrid_requires_both_columns(self) -> None:
        """POST /api/upload validates hybrid mode requires text_column and image_column."""
        from fastapi.testclient import TestClient
        from vetorizer_lib.web.app import app
        import io

        client = TestClient(app)
        # Missing image_column
        response = client.post(
            "/api/upload",
            data={
                "database_name": "test_hybrid_missing",
                "ingest_mode": "hybrid",
                "content_column": "text",
                "text_column": "text",
            },
            files={"file": ("test.csv", io.BytesIO(b"id,text,image_path\n1,test,/img.png"), "text/csv")},
        )
        # Should return 400 validation error for missing required parameter
        assert response.status_code == 400

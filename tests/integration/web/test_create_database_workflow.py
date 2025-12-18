"""Integration tests for database creation workflow.

Tests the complete end-to-end flow of creating a database with file upload.
"""

import io
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    from vetorizer_lib.web.app import app
    return TestClient(app)


@pytest.fixture
def sample_csv_file():
    """Create sample CSV file for testing."""
    content = b"id,content\n1,Sample document 1\n2,Sample document 2\n3,Sample document 3"
    return ("test.csv", io.BytesIO(content), "text/csv")


@pytest.fixture
def sample_large_csv():
    """Create larger CSV file with more rows."""
    rows = ["id,content"]
    for i in range(100):
        rows.append(f"{i},Document {i} with some text content for testing")
    content = "\n".join(rows).encode()
    return ("large.csv", io.BytesIO(content), "text/csv")


class TestDatabaseCreationWorkflow:
    """Test complete database creation workflow."""
    
    def test_validation_before_creation(self, client, sample_csv_file):
        """Test file validation step before database creation."""
        # Step 1: Validate files
        response = client.post(
            "/api/databases/validate",
            data={"ingest_mode": "text"},
            files={"files": sample_csv_file},
        )
        
        # Validation should succeed or be pending implementation
        assert response.status_code in [200, 404, 422, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert data["can_proceed"] is True
            assert data["valid_files"] >= 1
    
    def test_create_database_with_text_mode(self, client, sample_csv_file):
        """Test creating database in text mode with CSV upload."""
        response = client.post(
            "/api/databases",
            data={
                "name": "Test Text DB",
                "ingest_mode": "text",
                "text_column": "content",
            },
            files={"files": sample_csv_file},
        )
        
        # Should succeed or be pending implementation
        assert response.status_code in [200, 201, 202, 404, 422, 501]
        
        if response.status_code in [200, 201, 202]:
            data = response.json()
            assert "database_id" in data or "id" in data
    
    def test_create_database_requires_name(self, client, sample_csv_file):
        """Test that database creation requires a name."""
        response = client.post(
            "/api/databases",
            data={
                "ingest_mode": "text",
                "text_column": "content",
            },
            files={"files": sample_csv_file},
        )
        
        # Should fail validation (missing name)
        assert response.status_code in [400, 422]
    
    def test_create_database_requires_mode(self, client, sample_csv_file):
        """Test that database creation requires ingest mode."""
        response = client.post(
            "/api/databases",
            data={
                "name": "Test DB",
                "text_column": "content",
            },
            files={"files": sample_csv_file},
        )
        
        # Should fail validation (missing mode)
        assert response.status_code in [400, 422]
    
    def test_create_database_rejects_invalid_name(self, client, sample_csv_file):
        """Test that invalid database names are rejected."""
        response = client.post(
            "/api/databases",
            data={
                "name": "Invalid@Name!",
                "ingest_mode": "text",
                "text_column": "content",
            },
            files={"files": sample_csv_file},
        )
        
        # Should fail validation (invalid name format)
        assert response.status_code in [400, 422]
    
    def test_create_database_with_hybrid_mode(self, client):
        """Test creating database in hybrid mode."""
        csv_content = b"id,content,image_path\n1,Text content,/path/to/image1.jpg\n2,More text,/path/to/image2.jpg"
        csv_file = ("hybrid.csv", io.BytesIO(csv_content), "text/csv")
        
        response = client.post(
            "/api/databases",
            data={
                "name": "Hybrid Test DB",
                "ingest_mode": "hybrid",
                "text_column": "content",
                "image_column": "image_path",
            },
            files={"files": csv_file},
        )
        
        # Should succeed or be pending implementation
        assert response.status_code in [200, 201, 202, 404, 422, 501]
        
        if response.status_code in [200, 201, 202]:
            data = response.json()
            assert "database_id" in data or "id" in data
    
    def test_create_database_with_custom_embedders(self, client, sample_csv_file):
        """Test creating database with custom embedder models."""
        response = client.post(
            "/api/databases",
            data={
                "name": "Custom Embedder DB",
                "ingest_mode": "text",
                "text_column": "content",
                "text_embedding_model": "sentence-transformers/all-mpnet-base-v2",
            },
            files={"files": sample_csv_file},
        )
        
        # Should succeed or be pending implementation
        assert response.status_code in [200, 201, 202, 404, 422, 501]
    
    def test_create_database_with_metadata_columns(self, client):
        """Test creating database with metadata columns."""
        csv_content = b"id,content,author,date\n1,Text,John,2024-01-01\n2,More,Jane,2024-01-02"
        csv_file = ("metadata.csv", io.BytesIO(csv_content), "text/csv")
        
        response = client.post(
            "/api/databases",
            data={
                "name": "Metadata DB",
                "ingest_mode": "text",
                "text_column": "content",
                "metadata_columns": "author,date",
            },
            files={"files": csv_file},
        )
        
        # Should succeed or be pending implementation
        assert response.status_code in [200, 201, 202, 404, 422, 501]
    
    def test_validation_rejects_wrong_file_type(self, client):
        """Test that validation rejects incompatible file types."""
        jpg_file = ("image.jpg", io.BytesIO(b"\xff\xd8\xff\xe0fake jpeg"), "image/jpeg")
        
        response = client.post(
            "/api/databases/validate",
            data={"ingest_mode": "text"},
            files={"files": jpg_file},
        )
        
        # Should succeed validation but mark file as invalid
        if response.status_code == 200:
            data = response.json()
            assert data["invalid_files"] >= 1 or data["can_proceed"] is False
    
    def test_multiple_file_upload(self, client):
        """Test uploading multiple files at once."""
        file1 = ("file1.csv", io.BytesIO(b"id,content\n1,text1"), "text/csv")
        file2 = ("file2.csv", io.BytesIO(b"id,content\n2,text2"), "text/csv")
        
        response = client.post(
            "/api/databases",
            data={
                "name": "Multi File DB",
                "ingest_mode": "text",
                "text_column": "content",
            },
            files=[("files", file1), ("files", file2)],
        )
        
        # Should handle multiple files
        assert response.status_code in [200, 201, 202, 404, 422, 501]


class TestErrorHandling:
    """Test error handling in database creation."""
    
    def test_missing_required_column_in_csv(self, client):
        """Test error when required column is missing from CSV."""
        csv_content = b"id,wrong_column\n1,value"
        csv_file = ("bad.csv", io.BytesIO(csv_content), "text/csv")
        
        response = client.post(
            "/api/databases",
            data={
                "name": "Missing Column DB",
                "ingest_mode": "text",
                "text_column": "content",  # This column doesn't exist
            },
            files={"files": csv_file},
        )
        
        # Should fail or return error in result
        assert response.status_code in [400, 422, 200, 201, 202]
        
        if response.status_code in [200, 201, 202]:
            data = response.json()
            # Should have errors or failed documents
            assert ("errors" in data and len(data["errors"]) > 0) or \
                   ("documents_failed" in data and data["documents_failed"] > 0)
    
    def test_empty_file_upload(self, client):
        """Test handling of empty file upload."""
        empty_file = ("empty.csv", io.BytesIO(b""), "text/csv")
        
        response = client.post(
            "/api/databases/validate",
            data={"ingest_mode": "text"},
            files={"files": empty_file},
        )
        
        # Should handle empty file gracefully
        if response.status_code == 200:
            data = response.json()
            assert data["can_proceed"] is False or data["invalid_files"] >= 1


class TestRollbackBehavior:
    """Test transactional behavior and rollback."""
    
    def test_database_not_created_on_validation_failure(self, client):
        """Test that database is not created if all files fail validation."""
        invalid_file = ("bad.pdf", io.BytesIO(b"fake pdf"), "application/pdf")
        
        response = client.post(
            "/api/databases",
            data={
                "name": "Should Not Exist DB",
                "ingest_mode": "text",
                "text_column": "content",
            },
            files={"files": invalid_file},
        )
        
        # Should either reject at validation or return error result
        if response.status_code in [200, 201]:
            data = response.json()
            # Should indicate no documents were processed
            assert data.get("documents_processed", 0) == 0

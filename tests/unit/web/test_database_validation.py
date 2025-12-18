"""Unit tests for database creation validation logic."""

import pytest
from vetorizer_lib.web.models.schemas import (
    CreateDatabaseWithFilesRequest,
    IngestMode,
)


class TestDatabaseCreationValidation:
    """Test database creation request validation."""
    
    def test_valid_text_mode_request(self):
        """Test valid database creation request for text mode."""
        request = CreateDatabaseWithFilesRequest(
            name="Test Database",
            ingest_mode=IngestMode.TEXT,
            text_column="content",
        )
        
        assert request.name == "Test Database"
        assert request.ingest_mode == IngestMode.TEXT
        assert request.text_column == "content"
        assert request.text_embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    
    def test_valid_image_mode_request(self):
        """Test valid database creation request for image mode."""
        request = CreateDatabaseWithFilesRequest(
            name="Image DB",
            ingest_mode=IngestMode.IMAGE,
            image_column="image_path",
        )
        
        assert request.ingest_mode == IngestMode.IMAGE
        assert request.image_column == "image_path"
        assert request.image_embedding_model == "openai/clip-vit-base-patch16"
    
    def test_valid_hybrid_mode_request(self):
        """Test valid database creation request for hybrid mode."""
        request = CreateDatabaseWithFilesRequest(
            name="Hybrid DB",
            ingest_mode=IngestMode.HYBRID,
            text_column="content",
            image_column="image_path",
        )
        
        assert request.ingest_mode == IngestMode.HYBRID
        assert request.text_column == "content"
        assert request.image_column == "image_path"
    
    def test_invalid_name_with_special_chars(self):
        """Test that names with special characters are rejected."""
        with pytest.raises(ValueError, match="alphanumeric"):
            CreateDatabaseWithFilesRequest(
                name="Test@Database!",
                ingest_mode=IngestMode.TEXT,
                text_column="content",
            )
    
    def test_valid_name_with_spaces_and_hyphens(self):
        """Test that spaces and hyphens are allowed in names."""
        request = CreateDatabaseWithFilesRequest(
            name="Test Database-2024",
            ingest_mode=IngestMode.TEXT,
            text_column="content",
        )
        
        assert request.name == "Test Database-2024"
    
    def test_custom_embedder_models(self):
        """Test custom embedder model configuration."""
        request = CreateDatabaseWithFilesRequest(
            name="Custom Models",
            ingest_mode=IngestMode.HYBRID,
            text_column="content",
            image_column="image",
            text_embedding_model="sentence-transformers/all-mpnet-base-v2",
            image_embedding_model="openai/clip-vit-large-patch14",
        )
        
        assert request.text_embedding_model == "sentence-transformers/all-mpnet-base-v2"
        assert request.image_embedding_model == "openai/clip-vit-large-patch14"
    
    def test_metadata_columns(self):
        """Test metadata columns configuration."""
        request = CreateDatabaseWithFilesRequest(
            name="With Metadata",
            ingest_mode=IngestMode.TEXT,
            text_column="content",
            metadata_columns=["author", "date", "category"],
        )
        
        assert request.metadata_columns == ["author", "date", "category"]
    
    def test_id_column_optional(self):
        """Test that id_column is optional."""
        request = CreateDatabaseWithFilesRequest(
            name="No ID Column",
            ingest_mode=IngestMode.TEXT,
            text_column="content",
        )
        
        assert request.id_column is None


class TestIngestionResultModel:
    """Test IngestionResult model."""
    
    def test_successful_ingestion_result(self):
        """Test successful ingestion result."""
        from vetorizer_lib.web.models.schemas import IngestionResult
        
        result = IngestionResult(
            database_id="db_123",
            database_name="Test DB",
            total_files=1,
            documents_processed=100,
            documents_ignored=5,
            documents_failed=2,
            processing_time_seconds=45.5,
        )
        
        assert result.database_id == "db_123"
        assert result.documents_processed == 100
        assert result.documents_ignored == 5
        assert result.documents_failed == 2
        assert len(result.errors) == 0
    
    def test_failed_ingestion_with_errors(self):
        """Test ingestion result with errors."""
        from vetorizer_lib.web.models.schemas import IngestionResult
        
        result = IngestionResult(
            database_id="db_456",
            database_name="Failed DB",
            total_files=1,
            documents_processed=0,
            documents_ignored=0,
            documents_failed=10,
            processing_time_seconds=5.0,
            errors=["Column 'content' not found", "Invalid image paths"],
        )
        
        assert result.documents_failed == 10
        assert len(result.errors) == 2
        assert "content" in result.errors[0]

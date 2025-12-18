"""Pydantic schemas for the web API.

This module defines all request/response schemas and enums used by the web API.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator
import re


class DatabaseStatus(str, Enum):
    """Status of a vector database."""

    CREATING = "CREATING"
    READY = "READY"
    UPDATING = "UPDATING"
    DELETING = "DELETING"
    FAILED = "FAILED"


class UploadStatus(str, Enum):
    """Status of an upload job."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class QueryType(str, Enum):
    """Type of search query."""

    TEXT = "text"
    IMAGE = "image"
    HYBRID = "hybrid"


class IngestMode(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    HYBRID = "hybrid"


class ValidationStatus(str, Enum):
    """Status of file validation."""
    
    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"


# Request Schemas


class CreateDatabaseRequest(BaseModel):
    """Request to create a new vector database."""

    name: str = Field(..., min_length=1, max_length=100, description="Database name")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate database name format.

        Args:
            v: The name to validate.

        Returns:
            The validated name.

        Raises:
            ValueError: If name format is invalid.
        """
        if len(v) > 1 and not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9 -]*[a-zA-Z0-9]$", v):
            raise ValueError("Name must be alphanumeric with spaces/hyphens, starting and ending with alphanumeric")
        if len(v) == 1 and not v.isalnum():
            raise ValueError("Single character name must be alphanumeric")
        return v


class UpdateDatabaseRequest(BaseModel):
    """Request to update a vector database."""

    name: str = Field(..., min_length=1, max_length=100, description="New database name")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate database name format."""
        if len(v) > 1 and not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9 -]*[a-zA-Z0-9]$", v):
            raise ValueError("Name must be alphanumeric with spaces/hyphens")
        return v


class FileValidationResult(BaseModel):
    """Result of validating a single file.
    
    Attributes:
        filename: Name of the file.
        status: Validation status (valid/warning/invalid).
        errors: List of error messages if validation failed.
        warnings: List of warning messages (non-blocking).
        file_size_bytes: Size of the file in bytes.
        mime_type: Detected MIME type.
    """
    
    filename: str
    status: ValidationStatus
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    file_size_bytes: int
    mime_type: str | None = None


class BatchValidationSummary(BaseModel):
    """Summary of batch file validation.
    
    Attributes:
        overall_status: Overall validation status (valid if all valid, partial if mixed, invalid if all invalid).
        total_files: Total number of files in batch.
        valid_files: Number of valid files.
        warning_files: Number of files with warnings.
        invalid_files: Number of invalid files.
        files: Detailed validation results per file.
        can_proceed: Whether user can proceed with creation (true if at least one valid file).
        summary_message: Human-readable summary.
    """
    
    overall_status: ValidationStatus
    total_files: int
    valid_files: int
    warning_files: int
    invalid_files: int
    files: list[FileValidationResult]
    can_proceed: bool
    summary_message: str


class CreateDatabaseWithFilesRequest(BaseModel):
    """Request to create database with initial file upload.
    
    This extends database creation to include file upload in a single operation.
    Files are validated before database creation proceeds.
    
    Attributes:
        name: Database name.
        ingest_mode: Mode for ingestion (text/image/hybrid).
        text_embedding_model: Model for text embeddings (optional, uses default if not specified).
        image_embedding_model: Model for image embeddings (optional, uses default if not specified).
        text_column: Column name for text content (required for text/hybrid modes).
        image_column: Column name for image paths/URLs (required for image/hybrid modes).
        id_column: Optional column name for document IDs.
        metadata_columns: Optional list of column names to include as metadata.
    """
    
    name: str = Field(..., min_length=1, max_length=100)
    ingest_mode: IngestMode
    text_embedding_model: str | None = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    image_embedding_model: str | None = Field(default="openai/clip-vit-base-patch16")
    text_column: str | None = None
    image_column: str | None = None
    id_column: str | None = None
    metadata_columns: list[str] | None = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate database name format."""
        if len(v) > 1 and not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9 -]*[a-zA-Z0-9]$", v):
            raise ValueError("Name must be alphanumeric with spaces/hyphens, starting and ending with alphanumeric")
        if len(v) == 1 and not v.isalnum():
            raise ValueError("Single character name must be alphanumeric")
        return v


class IngestionResult(BaseModel):
    """Result of database creation with ingestion.
    
    Attributes:
        database_id: ID of created database.
        database_name: Name of created database.
        total_files: Total files processed.
        documents_processed: Number of documents successfully ingested.
        documents_ignored: Number of documents ignored (e.g., missing required columns).
        documents_failed: Number of documents that failed processing.
        processing_time_seconds: Total processing time.
        errors: List of error messages if any failures occurred.
    """
    
    database_id: str
    database_name: str
    total_files: int
    documents_processed: int
    documents_ignored: int
    documents_failed: int
    processing_time_seconds: float
    errors: list[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    """Request to search vector databases."""

    database_ids: list[str] = Field(..., min_length=1, max_length=4, description="Database IDs to search")
    query_type: QueryType = Field(..., description="Type of query (text or image)")
    query_content: str = Field(..., min_length=1, description="Query content")
    limit: int = Field(default=10, ge=1, le=100, description="Max results per database")
    min_score: float | None = Field(default=None, ge=0.0, le=1.0, description="Minimum similarity score")


# Response Schemas


class VectorDatabaseResponse(BaseModel):
    """Response containing vector database details."""

    id: str
    name: str
    collection_name: str
    document_count: int
    embedding_model: str
    embedding_dimension: int
    ingest_mode: IngestMode = IngestMode.TEXT
    text_embedding_model: str | None = None
    image_embedding_model: str | None = None
    text_embedding_dimension: int | None = None
    image_embedding_dimension: int | None = None
    status: DatabaseStatus
    created_at: datetime
    updated_at: datetime


class UploadJobResponse(BaseModel):
    """Response containing upload job details."""

    id: str
    database_id: str
    filename: str
    file_size_bytes: int
    content_column: str
    ingest_mode: IngestMode = IngestMode.TEXT
    text_column: str | None = None
    image_column: str | None = None
    id_column: str | None = None
    metadata_columns: list[str] | None = None
    status: UploadStatus
    progress_percent: int = 0
    documents_processed: int = 0
    documents_failed: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class SearchResultItem(BaseModel):
    """A single search result item."""

    id: str
    content: str
    score: float
    metadata: dict[str, Any] | None = None
    database_id: str
    database_name: str


class SearchResponse(BaseModel):
    """Response containing search results."""

    query_id: str
    results: dict[str, list[SearchResultItem]]
    total_results: int
    query_time_ms: int


class ColumnPreviewResponse(BaseModel):
    """Response containing CSV column preview."""

    columns: list[str]
    row_count: int
    sample_rows: list[dict[str, Any]]


class ErrorDetail(BaseModel):
    """Error detail information."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: ErrorDetail

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


class IngestMode(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    HYBRID = "hybrid"


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

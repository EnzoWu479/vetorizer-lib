"""Document and result dataclasses for vetorizer_lib.

This module contains the core data structures for documents, search results,
and ingestion results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ContentType(str, Enum):
    """Type of content being embedded.

    Attributes:
        TEXT: Text content.
        IMAGE: Image file path.

    Example:
        >>> content_type = ContentType.TEXT
        >>> print(content_type.value)
        text
    """

    TEXT = "text"
    IMAGE = "image"


@dataclass
class Document:
    """A single item to be embedded and stored in the vector database.

    Args:
        id: Unique identifier for the document.
        content: Text content or image file path.
        content_type: Type of content (text or image).
        embedding: Vector representation (generated during embedding).
        metadata: Additional key-value data.

    Example:
        >>> doc = Document(
        ...     id="doc-001",
        ...     content="A great product description",
        ...     content_type=ContentType.TEXT,
        ...     metadata={"title": "Product A"}
        ... )
        >>> print(doc.id)
        doc-001
    """

    id: str
    content: str
    content_type: ContentType = ContentType.TEXT
    embedding: list[float] = field(default_factory=list)
    modalities: list[str] = field(default_factory=list)
    composition_metadata: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """A single search result from vector similarity search.

    Args:
        id: Document ID.
        score: Similarity score (0.0 to 1.0 for cosine).
        content: Original content.
        metadata: Document metadata.

    Example:
        >>> result = SearchResult(
        ...     id="doc-001",
        ...     score=0.95,
        ...     content="A great product",
        ...     metadata={"title": "Product A"}
        ... )
        >>> print(f"{result.score:.2f}")
        0.95
    """

    id: str
    score: float
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestResult:
    """Result of an ingestion operation.

    Args:
        processed: Number of successfully ingested documents.
        skipped: Number of skipped documents (empty content, etc.).
        failed: Number of failed documents.
        errors: Error messages for failed items.
        duration_seconds: Total processing time in seconds.

    Example:
        >>> result = IngestResult(
        ...     processed=100,
        ...     skipped=5,
        ...     failed=0,
        ...     errors=[],
        ...     duration_seconds=12.5
        ... )
        >>> print(f"Ingested {result.processed} documents")
        Ingested 100 documents
    """

    processed: int
    skipped: int
    failed: int
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0

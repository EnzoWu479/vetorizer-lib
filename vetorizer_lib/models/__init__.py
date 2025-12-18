"""Data models for vetorizer_lib.

This module exports all dataclasses, enums, and configuration objects.
"""

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

__all__ = [
    "ContentType",
    "Modality",
    "DistanceMetric",
    "Document",
    "SearchResult",
    "IngestResult",
    "VectorStoreConfig",
    "IngestConfig",
]

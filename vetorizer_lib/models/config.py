"""Configuration dataclasses and enums for vetorizer_lib.

This module contains configuration objects for embedding models, vector stores,
and ingestion processes.
"""

from dataclasses import dataclass, field
from enum import Enum


class Modality(str, Enum):
    """Embedding model modality.

    Attributes:
        TEXT: Text-only embeddings (e.g., sentence-transformers).
        IMAGE: Image-only embeddings.
        MULTIMODAL: Text and image embeddings (e.g., CLIP).

    Example:
        >>> model_modality = Modality.TEXT
        >>> print(model_modality.value)
        text
    """

    TEXT = "text"
    IMAGE = "image"
    MULTIMODAL = "multimodal"


class IngestMode(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    HYBRID = "hybrid"


class SearchMode(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    HYBRID = "hybrid"


class DistanceMetric(str, Enum):
    """Vector similarity distance metric.

    Attributes:
        COSINE: Cosine similarity (default, normalized).
        EUCLIDEAN: Euclidean distance.
        DOT: Dot product similarity.

    Example:
        >>> metric = DistanceMetric.COSINE
        >>> print(metric.value)
        cosine
    """

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT = "dot"


@dataclass
class VectorStoreConfig:
    """Configuration for connecting to a vector database.

    Args:
        url: Qdrant server URL. If None, uses local storage.
        api_key: API key for Qdrant Cloud authentication.
        collection_name: Name of the Qdrant collection.
        distance_metric: Similarity metric for vector comparison.
        path: Local storage path for file-based Qdrant.

    Example:
        >>> config = VectorStoreConfig(
        ...     url="http://localhost:6333",
        ...     collection_name="products"
        ... )
        >>> print(config.collection_name)
        products
    """

    url: str | None = None
    api_key: str | None = None
    collection_name: str = "default"
    distance_metric: DistanceMetric = DistanceMetric.COSINE
    path: str | None = None


@dataclass
class IngestConfig:
    """Configuration for CSV ingestion.

    Args:
        file_path: Path to the CSV file.
        content_column: Column containing content to embed (text content for text/hybrid mode).
        id_column: Column for document IDs. Auto-generates UUIDs if None.
        metadata_columns: Additional columns to store as metadata.
        batch_size: Number of documents to process per batch.
        skip_empty: Skip rows where content_column is empty.
        image_column: Column containing image paths (required for image/hybrid mode).
        base_path: Base directory for resolving relative paths in image_column.

    Example:
        >>> config = IngestConfig(
        ...     file_path="data.csv",
        ...     content_column="description",
        ...     metadata_columns=["title", "category"]
        ... )
        >>> print(config.batch_size)
        100
        >>> # Hybrid mode example
        >>> hybrid_config = IngestConfig(
        ...     file_path="data.csv",
        ...     content_column="text",
        ...     image_column="image_path",
        ...     batch_size=32
        ... )
    """

    file_path: str
    content_column: str
    id_column: str | None = None
    metadata_columns: list[str] = field(default_factory=list)
    batch_size: int = 100
    skip_empty: bool = True
    image_column: str | None = None
    base_path: str | None = None

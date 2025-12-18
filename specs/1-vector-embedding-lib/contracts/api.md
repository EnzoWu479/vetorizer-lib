# API Contract: Vector Embedding Library

**Feature**: 1-vector-embedding-lib  
**Date**: 2025-12-17  
**Version**: 0.1.0

## Public API

### VetorizerClient

The main entry point for the library.

#### Constructor

```python
def __init__(
    self,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    qdrant_url: str | None = None,
    qdrant_api_key: str | None = None,
    qdrant_path: str | None = None,
    collection_name: str = "default",
    distance_metric: Literal["cosine", "euclidean", "dot"] = "cosine",
) -> None:
    """Initialize the Vetorizer client.

    Args:
        model_name: HuggingFace model identifier for embeddings.
        qdrant_url: Qdrant server URL. If None, uses local storage.
        qdrant_api_key: API key for Qdrant Cloud.
        qdrant_path: Local path for file-based Qdrant. If None with no URL, uses in-memory.
        collection_name: Name of the Qdrant collection.
        distance_metric: Similarity metric for vector comparison.

    Raises:
        ConfigurationError: If configuration is invalid.
        ModelLoadError: If the embedding model cannot be loaded.
        ConnectionError: If Qdrant is unreachable.

    Example:
        >>> client = VetorizerClient()  # In-memory, default model
        >>> client = VetorizerClient(qdrant_url="http://localhost:6333")
    """
```

---

### ingest_csv

```python
def ingest_csv(
    self,
    file_path: str | Path,
    content_column: str,
    id_column: str | None = None,
    metadata_columns: list[str] | None = None,
    batch_size: int = 100,
    skip_empty: bool = True,
    on_progress: Callable[[int, int], None] | None = None,
) -> IngestResult:
    """Ingest data from a CSV file into the vector database.

    Args:
        file_path: Path to the CSV file.
        content_column: Name of the column containing text to embed.
        id_column: Column for document IDs. Auto-generates UUIDs if None.
        metadata_columns: Additional columns to store as metadata.
        batch_size: Number of documents to process per batch.
        skip_empty: Skip rows where content_column is empty.
        on_progress: Callback function(processed, total) for progress updates.

    Returns:
        IngestResult with counts of processed, skipped, and failed documents.

    Raises:
        IngestError: If the file cannot be read or processed.
        ConfigurationError: If content_column doesn't exist.

    Example:
        >>> result = client.ingest_csv(
        ...     "data.csv",
        ...     content_column="description",
        ...     metadata_columns=["title", "category"]
        ... )
        >>> print(f"Ingested {result.processed} documents")
    """
```

---

### search

```python
def search(
    self,
    query: str,
    limit: int = 10,
    min_score: float | None = None,
    filter: dict[str, Any] | None = None,
) -> list[SearchResult]:
    """Search the vector database for similar content.

    Args:
        query: Text query to search for.
        limit: Maximum number of results to return.
        min_score: Minimum similarity score threshold (0.0 to 1.0).
        filter: Metadata filter conditions.

    Returns:
        List of SearchResult objects sorted by similarity (highest first).

    Raises:
        SearchError: If the search fails.
        ConfigurationError: If the collection doesn't exist.

    Example:
        >>> results = client.search("machine learning", limit=5)
        >>> for r in results:
        ...     print(f"{r.score:.2f}: {r.content[:50]}...")
    """
```

---

### search_by_image

```python
def search_by_image(
    self,
    image_path: str | Path,
    limit: int = 10,
    min_score: float | None = None,
    filter: dict[str, Any] | None = None,
) -> list[SearchResult]:
    """Search the vector database using an image query.

    Requires a multimodal model (e.g., CLIP) to be configured.

    Args:
        image_path: Path to the query image.
        limit: Maximum number of results to return.
        min_score: Minimum similarity score threshold.
        filter: Metadata filter conditions.

    Returns:
        List of SearchResult objects sorted by similarity.

    Raises:
        SearchError: If the search fails.
        ConfigurationError: If model doesn't support image embeddings.

    Example:
        >>> results = client.search_by_image("query.jpg", limit=5)
    """
```

---

### ingest_images

```python
def ingest_images(
    self,
    file_path: str | Path,
    image_column: str,
    id_column: str | None = None,
    metadata_columns: list[str] | None = None,
    batch_size: int = 32,
    on_progress: Callable[[int, int], None] | None = None,
) -> IngestResult:
    """Ingest images from a CSV file into the vector database.

    The CSV should contain paths to image files.
    Requires a multimodal model (e.g., CLIP) to be configured.

    Args:
        file_path: Path to the CSV file.
        image_column: Column containing image file paths.
        id_column: Column for document IDs.
        metadata_columns: Additional columns to store as metadata.
        batch_size: Number of images to process per batch.
        on_progress: Callback for progress updates.

    Returns:
        IngestResult with processing statistics.

    Raises:
        IngestError: If images cannot be loaded or processed.
        ConfigurationError: If model doesn't support image embeddings.

    Example:
        >>> client = VetorizerClient(model_name="openai/clip-vit-base-patch32")
        >>> result = client.ingest_images("images.csv", image_column="path")
    """
```

---

## Data Classes

### IngestResult

```python
@dataclass
class IngestResult:
    """Result of an ingestion operation."""
    processed: int      # Successfully ingested documents
    skipped: int        # Skipped (empty content, etc.)
    failed: int         # Failed to process
    errors: list[str]   # Error messages for failed items
    duration_seconds: float  # Total processing time
```

### SearchResult

```python
@dataclass
class SearchResult:
    """A single search result."""
    id: str                    # Document ID
    score: float               # Similarity score (0.0 to 1.0)
    content: str               # Original content
    metadata: dict[str, Any]   # Document metadata
```

---

## Exceptions

```python
class VetorizerError(Exception):
    """Base exception for all Vetorizer errors."""

class ConfigurationError(VetorizerError):
    """Invalid configuration or missing parameters."""

class ConnectionError(VetorizerError):
    """Cannot connect to Qdrant."""

class ModelLoadError(VetorizerError):
    """Cannot load the embedding model."""

class IngestError(VetorizerError):
    """Error during data ingestion."""

class SearchError(VetorizerError):
    """Error during search operation."""
```

---

## Usage Patterns

### Minimal Example (Text)

```python
from vetorizer_lib import VetorizerClient

client = VetorizerClient()
client.ingest_csv("products.csv", content_column="description")
results = client.search("comfortable running shoes")
```

### With Qdrant Server

```python
client = VetorizerClient(
    qdrant_url="http://localhost:6333",
    collection_name="products"
)
```

### Image Search with CLIP

```python
client = VetorizerClient(
    model_name="openai/clip-vit-base-patch32",
    collection_name="images"
)
client.ingest_images("catalog.csv", image_column="image_path")
results = client.search("a red sports car")  # Text-to-image search
```

### Progress Tracking

```python
def on_progress(processed: int, total: int) -> None:
    print(f"Progress: {processed}/{total} ({100*processed/total:.1f}%)")

client.ingest_csv("large_data.csv", content_column="text", on_progress=on_progress)
```

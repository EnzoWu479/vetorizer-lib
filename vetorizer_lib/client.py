"""Main VetorizerClient class for embedding and searching.

This module contains the primary interface for the vetorizer library.
"""

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from vetorizer_lib.embedders.text import TextEmbedder
from vetorizer_lib.ingest.csv import read_csv_batches
from vetorizer_lib.models.config import DistanceMetric, IngestConfig
from vetorizer_lib.models.document import ContentType, IngestResult, SearchResult
from vetorizer_lib.stores.qdrant import QdrantStore


class VetorizerClient:
    """Main client for embedding text/images and searching in Qdrant.

    This class provides a high-level interface for:
    - Ingesting CSV data into a vector database
    - Searching for semantically similar content
    - Configuring embedding models

    Args:
        model_name: HuggingFace model identifier for embeddings.
        qdrant_url: Qdrant server URL. If None, uses local storage.
        qdrant_api_key: API key for Qdrant Cloud.
        qdrant_path: Local path for file-based Qdrant.
        collection_name: Name of the Qdrant collection.
        distance_metric: Similarity metric for vector comparison.

    Example:
        >>> client = VetorizerClient()
        >>> client.ingest_csv("data.csv", content_column="description")
        >>> results = client.search("machine learning")
    """

    DISTANCE_MAP = {
        "cosine": DistanceMetric.COSINE,
        "euclidean": DistanceMetric.EUCLIDEAN,
        "dot": DistanceMetric.DOT,
    }

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        qdrant_url: str | None = None,
        qdrant_api_key: str | None = None,
        qdrant_path: str | None = None,
        collection_name: str = "default",
        distance_metric: Literal["cosine", "euclidean", "dot"] = "cosine",
    ) -> None:
        """Initialize the Vetorizer client."""
        self._model_name = model_name
        self._qdrant_url = qdrant_url
        self._qdrant_api_key = qdrant_api_key
        self._qdrant_path = qdrant_path
        self._collection_name = collection_name
        self._distance_metric = self.DISTANCE_MAP.get(distance_metric, DistanceMetric.COSINE)

        # Initialize embedder and store lazily
        self._embedder: TextEmbedder | None = None
        self._image_embedder: Any = None  # ImageEmbedder, lazy import
        self._store: QdrantStore | None = None

    def _get_embedder(self) -> TextEmbedder:
        """Get or create the text embedder."""
        if self._embedder is None:
            self._embedder = TextEmbedder(model_name=self._model_name)
        return self._embedder

    def _get_store(self) -> QdrantStore:
        """Get or create the vector store."""
        if self._store is None:
            self._store = QdrantStore(
                url=self._qdrant_url,
                api_key=self._qdrant_api_key,
                path=self._qdrant_path,
                collection_name=self._collection_name,
                distance_metric=self._distance_metric,
            )
        return self._store

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
        """
        start_time = time.time()

        config = IngestConfig(
            file_path=str(file_path),
            content_column=content_column,
            id_column=id_column,
            metadata_columns=metadata_columns or [],
            batch_size=batch_size,
            skip_empty=skip_empty,
        )

        embedder = self._get_embedder()
        store = self._get_store()

        processed = 0
        skipped = 0
        failed = 0
        errors: list[str] = []

        # Count total rows for progress (optional)
        total = 0
        if on_progress:
            import pandas as pd
            try:
                total = len(pd.read_csv(file_path))
            except Exception:
                total = 0

        for batch in read_csv_batches(config, ContentType.TEXT):
            try:
                # Generate embeddings for batch
                texts = [doc.content for doc in batch]
                embeddings = embedder.embed(texts)

                # Attach embeddings to documents
                for doc, embedding in zip(batch, embeddings):
                    doc.embedding = embedding

                # Store in vector database
                store.upsert(batch)
                processed += len(batch)

                if on_progress and total > 0:
                    on_progress(processed, total)

            except Exception as e:
                failed += len(batch)
                errors.append(f"Batch failed: {e}")

        duration = time.time() - start_time

        return IngestResult(
            processed=processed,
            skipped=skipped,
            failed=failed,
            errors=errors,
            duration_seconds=duration,
        )

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
        """
        embedder = self._get_embedder()
        store = self._get_store()

        # Embed the query
        query_vectors = embedder.embed([query])
        query_vector = query_vectors[0]

        # Search the store
        return store.search(
            vector=query_vector,
            limit=limit,
            min_score=min_score,
            filter=filter,
        )

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
        """
        start_time = time.time()

        config = IngestConfig(
            file_path=str(file_path),
            content_column=image_column,
            id_column=id_column,
            metadata_columns=metadata_columns or [],
            batch_size=batch_size,
            skip_empty=True,
        )

        embedder = self._get_image_embedder()
        store = self._get_store()

        processed = 0
        skipped = 0
        failed = 0
        errors: list[str] = []

        for batch in read_csv_batches(config, ContentType.IMAGE):
            try:
                # Generate embeddings for batch
                image_paths = [doc.content for doc in batch]
                embeddings = embedder.embed_image(image_paths)

                # Attach embeddings to documents
                for doc, embedding in zip(batch, embeddings):
                    doc.embedding = embedding

                # Store in vector database
                store.upsert(batch)
                processed += len(batch)

                if on_progress:
                    on_progress(processed, processed)

            except Exception as e:
                failed += len(batch)
                errors.append(f"Batch failed: {e}")

        duration = time.time() - start_time

        return IngestResult(
            processed=processed,
            skipped=skipped,
            failed=failed,
            errors=errors,
            duration_seconds=duration,
        )

    def search_by_image(
        self,
        image_path: str | Path,
        limit: int = 10,
        min_score: float | None = None,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Search the vector database using an image query.

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
        """
        embedder = self._get_image_embedder()
        store = self._get_store()

        # Embed the query image
        query_vectors = embedder.embed_image([str(image_path)])
        query_vector = query_vectors[0]

        # Search the store
        return store.search(
            vector=query_vector,
            limit=limit,
            min_score=min_score,
            filter=filter,
        )

    def _get_image_embedder(self) -> Any:
        """Get or create the image embedder."""
        from vetorizer_lib.embedders.image import ImageEmbedder

        if self._image_embedder is None:
            self._image_embedder = ImageEmbedder(model_name=self._model_name)
        return self._image_embedder

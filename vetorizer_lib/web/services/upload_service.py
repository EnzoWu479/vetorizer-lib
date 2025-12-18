"""Upload service for CSV file processing and ingestion.

This module provides functions for handling CSV uploads, creating upload jobs,
and processing data into vector databases using Qdrant-based MetadataStore.
"""

import asyncio
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from vetorizer_lib.web.models.metadata_store import MetadataStore
from vetorizer_lib.web.models.schemas import DatabaseStatus, IngestMode, UploadStatus, UploadJobResponse


def create_upload_job(
    store: MetadataStore,
    database_id: str,
    filename: str,
    file_size_bytes: int,
    content_column: str,
    ingest_mode: IngestMode = IngestMode.TEXT,
    text_column: str | None = None,
    image_column: str | None = None,
    id_column: str | None = None,
    metadata_columns: list[str] | None = None,
) -> UploadJobResponse:
    """Create a new upload job entry.

    Args:
        store: MetadataStore instance.
        database_id: Target database UUID.
        filename: Original filename.
        file_size_bytes: File size in bytes.
        content_column: CSV column containing text to embed.
        id_column: Optional CSV column for document IDs.
        metadata_columns: Optional list of metadata columns.

    Returns:
        The created upload job response.

    Example:
        >>> store = MetadataStore(qdrant_path="./data/qdrant")
        >>> job = create_upload_job(store, "db-uuid", "data.csv", 1024, "description")
    """
    return store.create_upload_job(
        database_id=database_id,
        filename=filename,
        file_size_bytes=file_size_bytes,
        content_column=content_column,
        ingest_mode=ingest_mode,
        text_column=text_column,
        image_column=image_column,
        id_column=id_column,
        metadata_columns=metadata_columns,
    )


def get_upload_job(store: MetadataStore, job_id: str) -> UploadJobResponse | None:
    """Get an upload job by ID.

    Args:
        store: MetadataStore instance.
        job_id: The job UUID.

    Returns:
        The job response or None if not found.
    """
    return store.get_upload_job(job_id)


def update_job_progress(
    store: MetadataStore,
    job_id: str,
    progress_percent: int,
    documents_processed: int,
    documents_failed: int = 0,
) -> None:
    """Update the progress of an upload job.

    Args:
        store: MetadataStore instance.
        job_id: The job UUID.
        progress_percent: Current progress (0-100).
        documents_processed: Number of documents processed.
        documents_failed: Number of documents that failed.
    """
    store.update_upload_job(
        job_id=job_id,
        progress_percent=progress_percent,
        documents_processed=documents_processed,
        documents_failed=documents_failed,
    )


def update_job_status(
    store: MetadataStore,
    job_id: str,
    status: UploadStatus,
    error_message: str | None = None,
) -> None:
    """Update the status of an upload job.

    Args:
        store: MetadataStore instance.
        job_id: The job UUID.
        status: New status.
        error_message: Optional error message for failed status.
    """
    store.update_upload_job(
        job_id=job_id,
        status=status,
        error_message=error_message,
    )


def preview_csv_columns(file_path: Path, max_rows: int = 5) -> dict[str, Any]:
    """Preview CSV file columns and sample data.

    Args:
        file_path: Path to the CSV file.
        max_rows: Maximum number of sample rows to return.

    Returns:
        Dictionary with columns, row_count, and sample_rows.

    Raises:
        ValueError: If file is not a valid CSV.

    Example:
        >>> preview = preview_csv_columns(Path("data.csv"))
        >>> print(preview["columns"])
    """
    try:
        df = pd.read_csv(file_path, nrows=max_rows + 1)
        total_rows = len(pd.read_csv(file_path))

        return {
            "columns": list(df.columns),
            "row_count": total_rows,
            "sample_rows": df.head(max_rows).to_dict(orient="records"),
        }
    except Exception as e:
        raise ValueError(f"Invalid CSV file: {str(e)}")


async def process_csv(
    store: MetadataStore,
    job_id: str,
    database_id: str,
    file_path: Path,
    content_column: str,
    collection_name: str,
    ingest_mode: IngestMode = IngestMode.TEXT,
    text_column: str | None = None,
    image_column: str | None = None,
    id_column: str | None = None,
    metadata_columns: list[str] | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    qdrant_url: str | None = None,
    qdrant_path: str | None = "./data/qdrant",
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> int:
    """Process a CSV file and ingest into vector database.

    Args:
        store: MetadataStore instance.
        job_id: Upload job UUID.
        database_id: Target database UUID.
        file_path: Path to the CSV file.
        content_column: CSV column containing text to embed.
        collection_name: Qdrant collection name.
        id_column: Optional CSV column for document IDs.
        metadata_columns: Optional list of metadata columns.
        progress_callback: Optional callback for progress updates.
        qdrant_url: URL for remote Qdrant server.
        qdrant_path: Path to Qdrant storage (local mode).
        embedding_model: Embedding model to use for this database.

    Returns:
        Number of documents successfully processed.

    Raises:
        ValueError: If content column not found or file is invalid.
    """
    from vetorizer_lib.client import VetorizerClient

    # Update job status to processing
    update_job_status(store, job_id, UploadStatus.PROCESSING)

    try:
        # Read CSV
        df = pd.read_csv(file_path)

        if ingest_mode == IngestMode.TEXT:
            if content_column not in df.columns:
                raise ValueError(f"Column '{content_column}' not found in CSV")
        elif ingest_mode == IngestMode.IMAGE:
            if content_column not in df.columns:
                raise ValueError(f"Column '{content_column}' not found in CSV")
        elif ingest_mode == IngestMode.HYBRID:
            if not text_column or not image_column:
                raise ValueError("For hybrid ingestion, text_column and image_column are required")
            if text_column not in df.columns:
                raise ValueError(f"Column '{text_column}' not found in CSV")
            if image_column not in df.columns:
                raise ValueError(f"Column '{image_column}' not found in CSV")

        total_rows = len(df)
        processed = 0
        failed = 0

        # Initialize vetorizer client with specified embedding model
        client = VetorizerClient(
            model_name=embedding_model,
            qdrant_url=qdrant_url,
            qdrant_path=qdrant_path,
            collection_name=collection_name,
        )

        try:
            if ingest_mode == IngestMode.TEXT:
                client.ingest_csv(
                    file_path=str(file_path),
                    content_column=content_column,
                    id_column=id_column,
                    metadata_columns=metadata_columns,
                )
            elif ingest_mode == IngestMode.IMAGE:
                client.ingest_images(
                    file_path=str(file_path),
                    image_column=content_column,
                    id_column=id_column,
                    metadata_columns=metadata_columns,
                )
            else:
                client.ingest_hybrid_csv(
                    file_path=str(file_path),
                    text_column=text_column or "",
                    image_column=image_column or "",
                    id_column=id_column,
                    metadata_columns=metadata_columns,
                )

            processed = total_rows
        except Exception:
            failed = total_rows

        progress = 100
        update_job_progress(store, job_id, progress, processed, failed)

        if progress_callback:
            progress_callback(progress, processed)

        await asyncio.sleep(0.01)

        # Get actual document count from the ingestion
        processed = total_rows - failed

        # Update final progress
        update_job_progress(store, job_id, 100, processed, failed)

        # Update job and database status
        update_job_status(store, job_id, UploadStatus.COMPLETED)
        store.update_database(database_id, status=DatabaseStatus.READY, document_count=processed)

        return processed

    except Exception as e:
        update_job_status(store, job_id, UploadStatus.FAILED, str(e))
        store.update_database(database_id, status=DatabaseStatus.FAILED)
        raise

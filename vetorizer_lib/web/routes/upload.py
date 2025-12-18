"""Upload routes for CSV file handling.

This module provides API endpoints for uploading CSV files,
previewing columns, and tracking upload progress.
"""

import asyncio
import tempfile
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, BackgroundTasks
from sse_starlette.sse import EventSourceResponse

from vetorizer_lib.web.deps import get_store, get_settings_dep
from vetorizer_lib.web.config import WebSettings
from vetorizer_lib.web.models.metadata_store import MetadataStore
from vetorizer_lib.web.models.schemas import (
    ColumnPreviewResponse,
    ErrorResponse,
    ErrorDetail,
    UploadJobResponse,
)
from vetorizer_lib.web.services.database_service import create_database, get_database_by_name
from vetorizer_lib.web.services.upload_service import (
    create_upload_job,
    get_upload_job,
    preview_csv_columns,
    process_csv,
)

router = APIRouter(prefix="/api", tags=["upload"])

# Store for tracking active upload progress
_upload_progress: dict[str, dict[str, Any]] = {}


@router.post("/columns", response_model=ColumnPreviewResponse)
async def preview_columns(
    file: UploadFile = File(...),
    settings: WebSettings = Depends(get_settings_dep),
) -> ColumnPreviewResponse:
    """Preview CSV file columns and sample data.

    Args:
        file: Uploaded CSV file.
        settings: Application settings.

    Returns:
        Column preview with names, row count, and sample rows.

    Raises:
        HTTPException: If file is invalid or too large.
    """
    # Check file size
    if file.size and file.size > settings.max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="FILE_TOO_LARGE",
                    message=f"File size exceeds maximum of {settings.max_upload_size // (1024*1024)}MB",
                )
            ).model_dump(),
        )

    # Check file type
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="INVALID_FILE",
                    message="File must be a CSV file",
                )
            ).model_dump(),
        )

    # Save to temp file and preview
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        preview = preview_csv_columns(tmp_path)
        return ColumnPreviewResponse(**preview)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="INVALID_FILE",
                    message=str(e),
                )
            ).model_dump(),
        )
    finally:
        tmp_path.unlink(missing_ok=True)


@router.post("/upload", response_model=UploadJobResponse, status_code=202)
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    database_name: str = Form(...),
    content_column: str = Form(...),
    id_column: str | None = Form(None),
    metadata_columns: str | None = Form(None),
    embedding_model: str | None = Form(None),
    overwrite: bool = Form(False),
    store: MetadataStore = Depends(get_store),
    settings: WebSettings = Depends(get_settings_dep),
) -> UploadJobResponse:
    """Upload a CSV file and create a vector database.

    Args:
        background_tasks: FastAPI background tasks.
        file: Uploaded CSV file.
        database_name: Name for the vector database.
        content_column: CSV column containing text to embed.
        id_column: Optional CSV column for document IDs.
        metadata_columns: Optional comma-separated list of metadata columns.
        embedding_model: Optional embedding model name (uses default if not provided).
        overwrite: Whether to overwrite existing database.
        store: MetadataStore instance.
        settings: Application settings.

    Returns:
        Upload job response with job ID for tracking.

    Raises:
        HTTPException: If file is invalid, too large, or database exists.
    """
    # Check file size
    if file.size and file.size > settings.max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="FILE_TOO_LARGE",
                    message=f"File size exceeds maximum of {settings.max_upload_size // (1024*1024)}MB",
                )
            ).model_dump(),
        )

    # Check file type
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="INVALID_FILE",
                    message="File must be a CSV file",
                )
            ).model_dump(),
        )

    # Check if database exists
    existing = get_database_by_name(store, database_name)
    if existing and not overwrite:
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="DUPLICATE_NAME",
                    message=f"Database '{database_name}' already exists. Set overwrite=true to replace.",
                )
            ).model_dump(),
        )

    # Parse metadata columns
    metadata_list = None
    if metadata_columns:
        metadata_list = [col.strip() for col in metadata_columns.split(",")]

    # Save uploaded file
    content = await file.read()
    file_size = len(content)

    # Create temp file for processing
    tmp_dir = Path(tempfile.gettempdir()) / "vetorizer_uploads"
    tmp_dir.mkdir(exist_ok=True)
    tmp_path = tmp_dir / f"{uuid.uuid4()}.csv"
    tmp_path.write_bytes(content)

    # Use provided embedding model or default from settings
    model_to_use = embedding_model if embedding_model else settings.embedding_model

    try:
        # Create database entry with embedding model
        database = create_database(store, database_name, embedding_model=model_to_use)

        # Create upload job
        job = create_upload_job(
            store=store,
            database_id=database.id,
            filename=file.filename or "upload.csv",
            file_size_bytes=file_size,
            content_column=content_column,
            id_column=id_column,
            metadata_columns=metadata_list,
        )

        # Initialize progress tracking
        _upload_progress[job.id] = {
            "percent": 0,
            "processed": 0,
            "status": "pending",
        }

        # Start background processing
        background_tasks.add_task(
            _process_upload,
            qdrant_url=settings.qdrant_url,
            qdrant_api_key=settings.qdrant_api_key,
            qdrant_path=str(settings.qdrant_path_resolved) if settings.qdrant_path_resolved else None,
            job_id=job.id,
            database_id=database.id,
            file_path=tmp_path,
            content_column=content_column,
            collection_name=database.collection_name,
            id_column=id_column,
            metadata_columns=metadata_list,
            embedding_model=model_to_use,
        )

        return job

    except ValueError as e:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="DUPLICATE_NAME",
                    message=str(e),
                )
            ).model_dump(),
        )


async def _process_upload(
    qdrant_url: str | None,
    qdrant_api_key: str | None,
    qdrant_path: str | None,
    job_id: str,
    database_id: str,
    file_path: Path,
    content_column: str,
    collection_name: str,
    id_column: str | None,
    metadata_columns: list[str] | None,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> None:
    """Background task to process CSV upload.

    Args:
        qdrant_url: URL for remote Qdrant server.
        qdrant_api_key: API key for Qdrant Cloud.
        qdrant_path: Path to Qdrant storage (local mode).
        job_id: Upload job UUID.
        database_id: Target database UUID.
        file_path: Path to uploaded CSV file.
        content_column: CSV column containing text to embed.
        collection_name: Qdrant collection name.
        id_column: Optional CSV column for document IDs.
        metadata_columns: Optional list of metadata columns.
        embedding_model: Embedding model to use for this database.
    """
    from vetorizer_lib.web.models.metadata_store import MetadataStore

    def progress_callback(percent: int, processed: int) -> None:
        _upload_progress[job_id] = {
            "percent": percent,
            "processed": processed,
            "status": "processing",
        }

    try:
        if qdrant_url:
            store = MetadataStore(qdrant_url=qdrant_url, qdrant_api_key=qdrant_api_key)
        else:
            store = MetadataStore(qdrant_path=qdrant_path)
        await process_csv(
            store=store,
            job_id=job_id,
            database_id=database_id,
            file_path=file_path,
            content_column=content_column,
            collection_name=collection_name,
            id_column=id_column,
            metadata_columns=metadata_columns,
            progress_callback=progress_callback,
            qdrant_url=qdrant_url,
            qdrant_path=qdrant_path,
            embedding_model=embedding_model,
        )
        _upload_progress[job_id]["status"] = "completed"
        _upload_progress[job_id]["percent"] = 100
    except Exception as e:
        _upload_progress[job_id] = {
            "percent": 0,
            "processed": 0,
            "status": "failed",
            "error": str(e),
        }
    finally:
        file_path.unlink(missing_ok=True)


@router.get("/upload/{job_id}", response_model=UploadJobResponse)
def get_upload_status(
    job_id: str,
    store: MetadataStore = Depends(get_store),
) -> UploadJobResponse:
    """Get the status of an upload job.

    Args:
        job_id: Upload job UUID.
        store: MetadataStore instance.

    Returns:
        Upload job response with current status.

    Raises:
        HTTPException: If job not found.
    """
    job = get_upload_job(store, job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="NOT_FOUND",
                    message=f"Upload job '{job_id}' not found",
                )
            ).model_dump(),
        )
    return job


@router.get("/upload/{job_id}/progress")
async def stream_upload_progress(job_id: str) -> EventSourceResponse:
    """Stream upload progress via Server-Sent Events.

    Args:
        job_id: Upload job UUID.

    Returns:
        SSE stream with progress updates.
    """
    async def event_generator():
        while True:
            progress = _upload_progress.get(job_id, {"percent": 0, "status": "unknown"})

            yield {
                "event": "progress",
                "data": str(progress),
            }

            if progress.get("status") in ("completed", "failed"):
                if progress.get("status") == "completed":
                    yield {"event": "completed", "data": str(progress)}
                else:
                    yield {"event": "error", "data": str(progress.get("error", "Unknown error"))}
                break

            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())

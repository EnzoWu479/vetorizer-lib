"""Database routes for vector database management.

This module provides API endpoints for listing, creating, updating,
and deleting vector databases.
"""

from fastapi import APIRouter, Depends, HTTPException

from vetorizer_lib.web.deps import get_store
from vetorizer_lib.web.models.metadata_store import MetadataStore
from vetorizer_lib.web.models.schemas import (
    CreateDatabaseRequest,
    UpdateDatabaseRequest,
    ErrorResponse,
    ErrorDetail,
    VectorDatabaseResponse,
)
from vetorizer_lib.web.services.database_service import (
    create_database,
    get_database,
    list_databases,
    update_database_name,
    delete_database,
)

router = APIRouter(prefix="/api/databases", tags=["databases"])


@router.get("", response_model=list[VectorDatabaseResponse])
def list_all_databases(
    store: MetadataStore = Depends(get_store),
) -> list[VectorDatabaseResponse]:
    """List all vector databases.

    Args:
        store: MetadataStore instance.

    Returns:
        List of all vector databases.
    """
    return list_databases(store)


@router.post("", response_model=VectorDatabaseResponse, status_code=201)
def create_new_database(
    request: CreateDatabaseRequest,
    store: MetadataStore = Depends(get_store),
) -> VectorDatabaseResponse:
    """Create a new empty vector database.

    Args:
        request: Database creation request with name.
        store: MetadataStore instance.

    Returns:
        Created database response.

    Raises:
        HTTPException: If database name already exists.
    """
    try:
        return create_database(store, request.name)
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="DUPLICATE_NAME",
                    message=str(e),
                )
            ).model_dump(),
        )


@router.get("/{database_id}", response_model=VectorDatabaseResponse)
def get_database_by_id(
    database_id: str,
    store: MetadataStore = Depends(get_store),
) -> VectorDatabaseResponse:
    """Get a vector database by ID.

    Args:
        database_id: Database UUID.
        store: MetadataStore instance.

    Returns:
        Database response.

    Raises:
        HTTPException: If database not found.
    """
    database = get_database(store, database_id)
    if not database:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="NOT_FOUND",
                    message=f"Database '{database_id}' not found",
                )
            ).model_dump(),
        )
    return database


@router.patch("/{database_id}", response_model=VectorDatabaseResponse)
def update_database(
    database_id: str,
    request: UpdateDatabaseRequest,
    store: MetadataStore = Depends(get_store),
) -> VectorDatabaseResponse:
    """Update a vector database (rename).

    Args:
        database_id: Database UUID.
        request: Update request with new name.
        store: MetadataStore instance.

    Returns:
        Updated database response.

    Raises:
        HTTPException: If database not found or new name exists.
    """
    # Check if database exists
    existing = get_database(store, database_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="NOT_FOUND",
                    message=f"Database '{database_id}' not found",
                )
            ).model_dump(),
        )

    try:
        updated = update_database_name(store, database_id, request.name)
        if not updated:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    error=ErrorDetail(
                        code="NOT_FOUND",
                        message=f"Database '{database_id}' not found",
                    )
                ).model_dump(),
            )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="DUPLICATE_NAME",
                    message=str(e),
                )
            ).model_dump(),
        )


@router.delete("/{database_id}", status_code=204)
def delete_database_by_id(
    database_id: str,
    store: MetadataStore = Depends(get_store),
) -> None:
    """Delete a vector database.

    Args:
        database_id: Database UUID.
        store: MetadataStore instance.

    Raises:
        HTTPException: If database not found.
    """
    deleted = delete_database(store, database_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="NOT_FOUND",
                    message=f"Database '{database_id}' not found",
                )
            ).model_dump(),
        )


# New endpoints for hybrid ingestion with file upload

from fastapi import File, UploadFile, Form
from vetorizer_lib.web.models.schemas import (
    BatchValidationSummary,
    IngestionResult,
    IngestMode,
)
from vetorizer_lib.web.services.validation_service import validate_file_batch


@router.post("/validate", response_model=BatchValidationSummary)
async def validate_files_for_database(
    ingest_mode: IngestMode = Form(...),
    files: list[UploadFile] = File(...),
) -> BatchValidationSummary:
    """Validate files before database creation.
    
    Validates uploaded files against the selected ingest mode and returns
    detailed validation summary.
    
    Args:
        ingest_mode: Mode for ingestion (text/image/hybrid).
        files: List of files to validate.
        
    Returns:
        BatchValidationSummary with validation results.
    """
    # Prepare files for validation
    file_handles: list[tuple[str, any]] = []
    for upload_file in files:
        file_handles.append((upload_file.filename or "unknown", upload_file.file))
    
    # Validate batch
    summary = await validate_file_batch(file_handles, ingest_mode)
    
    # Reset file positions
    for upload_file in files:
        await upload_file.seek(0)
    
    return summary

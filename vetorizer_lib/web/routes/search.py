"""Search routes for vector database queries.

This module provides API endpoints for searching vector databases
using text and image queries.
"""

import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from vetorizer_lib.web.deps import get_store, get_settings_dep
from vetorizer_lib.web.config import WebSettings
from vetorizer_lib.web.models.metadata_store import MetadataStore
from vetorizer_lib.web.models.schemas import (
    ErrorResponse,
    ErrorDetail,
    SearchRequest,
    SearchResponse,
    QueryType,
)
from vetorizer_lib.web.services.search_service import search_text, search_image

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("", response_model=SearchResponse)
def search_databases(
    request: SearchRequest,
    store: MetadataStore = Depends(get_store),
    settings: WebSettings = Depends(get_settings_dep),
) -> SearchResponse:
    """Search vector databases with text or image query.

    Args:
        request: Search request with database IDs, query type, and content.
        store: MetadataStore instance.
        settings: Application settings.

    Returns:
        Search response with results grouped by database.

    Raises:
        HTTPException: If database not found or search fails.
    """
    try:
        if request.query_type == QueryType.TEXT:
            return search_text(
                store=store,
                database_ids=request.database_ids,
                query=request.query_content,
                limit=request.limit,
                min_score=request.min_score,
                qdrant_url=settings.qdrant_url,
                qdrant_path=str(settings.qdrant_path_resolved) if settings.qdrant_path_resolved else None,
            )
        else:
            # For image queries via JSON, the content should be a file path or base64
            # This endpoint primarily handles text; use /search/image for file uploads
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error=ErrorDetail(
                        code="INVALID_QUERY_TYPE",
                        message="Use POST /api/search/image for image uploads",
                    )
                ).model_dump(),
            )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="NOT_FOUND",
                    message=str(e),
                )
            ).model_dump(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="SEARCH_ERROR",
                    message=f"Search failed: {str(e)}",
                )
            ).model_dump(),
        )


@router.post("/image", response_model=SearchResponse)
async def search_by_image(
    file: UploadFile = File(...),
    database_ids: str = Form(...),
    limit: int = Form(10),
    min_score: float | None = Form(None),
    store: MetadataStore = Depends(get_store),
    settings: WebSettings = Depends(get_settings_dep),
) -> SearchResponse:
    """Search vector databases using an image file.

    Args:
        file: Uploaded image file.
        database_ids: Comma-separated list of database UUIDs.
        limit: Maximum results per database.
        min_score: Minimum similarity score (0-1).
        store: MetadataStore instance.
        settings: Application settings.

    Returns:
        Search response with results grouped by database.

    Raises:
        HTTPException: If file is invalid or search fails.
    """
    # Validate file type
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    file_ext = Path(file.filename or "").suffix.lower()
    if file_ext not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="INVALID_FILE",
                    message=f"File must be an image ({', '.join(valid_extensions)})",
                )
            ).model_dump(),
        )

    # Parse database IDs
    db_ids = [id.strip() for id in database_ids.split(",")]
    if not db_ids or len(db_ids) > 4:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="INVALID_REQUEST",
                    message="Provide 1-4 database IDs",
                )
            ).model_dump(),
        )

    # Save uploaded file temporarily
    content = await file.read()
    tmp_path = Path(tempfile.gettempdir()) / f"vetorizer_search_{uuid.uuid4()}{file_ext}"
    tmp_path.write_bytes(content)

    try:
        return search_image(
            store=store,
            database_ids=db_ids,
            image_path=str(tmp_path),
            limit=limit,
            min_score=min_score,
            qdrant_url=settings.qdrant_url,
            qdrant_path=str(settings.qdrant_path_resolved) if settings.qdrant_path_resolved else None,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="NOT_FOUND",
                    message=str(e),
                )
            ).model_dump(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="SEARCH_ERROR",
                    message=f"Image search failed: {str(e)}",
                )
            ).model_dump(),
        )
    finally:
        tmp_path.unlink(missing_ok=True)

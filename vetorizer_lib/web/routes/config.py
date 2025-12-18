"""Configuration routes for read-only config display.

This module provides API endpoints for viewing the current
application configuration (read-only).
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from vetorizer_lib.web.deps import get_settings_dep
from vetorizer_lib.web.config import WebSettings


router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigResponse(BaseModel):
    """Read-only configuration response.

    Attributes:
        host: Host address the server is bound to.
        port: Port number the server is listening on.
        qdrant_url: URL for remote Qdrant server (if configured).
        qdrant_path: Path to Qdrant file-based storage (if using local mode).
        qdrant_mode: Either 'remote' or 'local'.
        max_upload_size: Maximum file upload size in bytes.
        max_upload_size_mb: Maximum file upload size in MB (for display).
        embedding_model: Default embedding model name.
        cors_origins: Allowed CORS origins.
    """

    host: str
    port: int
    qdrant_url: str | None
    qdrant_path: str | None
    qdrant_mode: str
    max_upload_size: int
    max_upload_size_mb: int
    embedding_model: str
    cors_origins: str


@router.get("", response_model=ConfigResponse)
def get_config(
    settings: WebSettings = Depends(get_settings_dep),
) -> ConfigResponse:
    """Get the current application configuration (read-only).

    Args:
        settings: Application settings.

    Returns:
        Current configuration values.
    """
    return ConfigResponse(
        host=settings.host,
        port=settings.port,
        qdrant_url=settings.qdrant_url,
        qdrant_path=str(settings.qdrant_path_resolved) if settings.qdrant_path_resolved else None,
        qdrant_mode="remote" if settings.qdrant_url else "local",
        max_upload_size=settings.max_upload_size,
        max_upload_size_mb=settings.max_upload_size // (1024 * 1024),
        embedding_model=settings.embedding_model,
        cors_origins=settings.cors_origins,
    )

"""Dependency injection for FastAPI routes.

This module provides dependency functions for MetadataStore
and vetorizer client instances.
"""

from vetorizer_lib.web.config import get_settings, WebSettings
from vetorizer_lib.web.models.metadata_store import MetadataStore


# Global metadata store instance
_metadata_store: MetadataStore | None = None


def get_store() -> MetadataStore:
    """Get the metadata store for use in route handlers.

    Returns:
        MetadataStore instance.

    Example:
        >>> @app.get("/databases")
        ... def list_databases(store: MetadataStore = Depends(get_store)):
        ...     return store.list_databases()
    """
    global _metadata_store
    if _metadata_store is None:
        settings = get_settings()
        if settings.qdrant_url:
            _metadata_store = MetadataStore(
                qdrant_url=settings.qdrant_url,
                qdrant_api_key=settings.qdrant_api_key,
            )
        else:
            _metadata_store = MetadataStore(qdrant_path=settings.qdrant_path)
    return _metadata_store


def get_settings_dep() -> WebSettings:
    """Get application settings for use in route handlers.

    Returns:
        WebSettings instance.

    Example:
        >>> @app.get("/config")
        ... async def get_config(settings: WebSettings = Depends(get_settings_dep)):
        ...     return {"max_upload_size": settings.max_upload_size}
    """
    return get_settings()


def init_metadata_store() -> None:
    """Initialize the metadata store on startup.

    This should be called during application startup to ensure
    the metadata collection is created.

    Example:
        >>> @app.on_event("startup")
        ... def startup():
        ...     init_metadata_store()
    """
    global _metadata_store
    settings = get_settings()
    if settings.qdrant_url:
        _metadata_store = MetadataStore(
            qdrant_url=settings.qdrant_url,
            qdrant_api_key=settings.qdrant_api_key,
        )
    else:
        _metadata_store = MetadataStore(qdrant_path=settings.qdrant_path)

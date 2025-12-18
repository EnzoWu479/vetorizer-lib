"""Web application configuration settings.

This module provides centralized configuration management for the web UI.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WebSettings(BaseSettings):
    """Web application settings loaded from environment variables.

    Attributes:
        host: Host address to bind the server to.
        port: Port number for the web server.
        qdrant_url: URL for remote Qdrant server (e.g., http://localhost:6333).
        qdrant_api_key: API key for Qdrant Cloud (optional).
        qdrant_path: Path to Qdrant file-based storage (used if qdrant_url is not set).
        cors_origins: Comma-separated list of allowed CORS origins.
        max_upload_size: Maximum file upload size in bytes (default 100MB).
        embedding_model: Default embedding model name.
        debug: Enable debug mode.

    Example:
        >>> settings = WebSettings()
        >>> settings.port
        8000
    """

    model_config = SettingsConfigDict(
        env_prefix="VETORIZER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False

    # Qdrant configuration
    qdrant_url: str | None = None  # Remote Qdrant URL (e.g., http://localhost:6333)
    qdrant_api_key: str | None = None  # API key for Qdrant Cloud
    qdrant_path: str = "./data/qdrant"  # Local file-based storage (used if qdrant_url is None)

    # CORS configuration
    cors_origins: str = "*"

    # Upload limits
    max_upload_size: int = 104857600  # 100MB

    # Embedding configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into a list.

        Returns:
            List of allowed origin URLs.
        """
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def qdrant_path_resolved(self) -> Path | None:
        """Get resolved Qdrant path for file-based storage.

        Returns:
            Absolute Path to Qdrant storage directory, or None if using remote URL.
        """
        if self.qdrant_url:
            return None
        path = Path(self.qdrant_path)
        path.mkdir(parents=True, exist_ok=True)
        return path.resolve()

    @property
    def is_remote_qdrant(self) -> bool:
        """Check if using remote Qdrant server.

        Returns:
            True if qdrant_url is configured.
        """
        return self.qdrant_url is not None

def get_settings() -> WebSettings:
    """Get application settings singleton.

    Returns:
        WebSettings instance.
    """
    return WebSettings()

"""Vetorizer Library - Embed text and images using HuggingFace models and store in Qdrant.

This library provides a simple interface for:
- Ingesting CSV data into a vector database
- Searching for semantically similar content
- Configuring embedding models from HuggingFace
- Supporting both text and image embeddings
"""

from vetorizer_lib.client import VetorizerClient
from vetorizer_lib.exceptions import (
    ConfigurationError,
    ConnectionError,
    IngestError,
    ModelLoadError,
    SearchError,
    VetorizerError,
)
from vetorizer_lib.models.document import Document, IngestResult, SearchResult

__version__ = "0.1.0"

__all__ = [
    "VetorizerClient",
    "Document",
    "SearchResult",
    "IngestResult",
    "VetorizerError",
    "ConfigurationError",
    "ConnectionError",
    "ModelLoadError",
    "IngestError",
    "SearchError",
]

"""Base protocol for embedders.

This module defines the Embedder protocol that all embedder implementations must follow.
"""

from typing import Protocol


class Embedder(Protocol):
    """Protocol for embedding text or images into vectors.

    All embedder implementations must provide these methods and properties.
    This enables dependency injection and easy mocking for tests.

    Attributes:
        dimension: The dimension of the output embedding vectors.
        model_name: The name/identifier of the embedding model.

    Example:
        >>> class MockEmbedder:
        ...     dimension = 384
        ...     model_name = "mock-model"
        ...     def embed(self, texts: list[str]) -> list[list[float]]:
        ...         return [[0.1] * 384 for _ in texts]
        ...
        >>> embedder: Embedder = MockEmbedder()
        >>> vectors = embedder.embed(["hello world"])
        >>> len(vectors[0])
        384
    """

    @property
    def dimension(self) -> int:
        """Return the dimension of embedding vectors."""
        ...

    @property
    def model_name(self) -> str:
        """Return the model name/identifier."""
        ...

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts into vectors.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors, one per input text.

        Raises:
            ModelLoadError: If the model is not loaded.
        """
        ...

    def embed_image(self, image_paths: list[str]) -> list[list[float]]:
        """Embed a list of images into vectors.

        Args:
            image_paths: List of paths to image files.

        Returns:
            List of embedding vectors, one per input image.

        Raises:
            ModelLoadError: If the model doesn't support image embedding.
            IngestError: If an image cannot be loaded.
        """
        ...

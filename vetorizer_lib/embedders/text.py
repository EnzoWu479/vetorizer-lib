"""Text embedder using sentence-transformers.

This module provides the TextEmbedder class for generating text embeddings
using HuggingFace sentence-transformers models.
"""

from sentence_transformers import SentenceTransformer

from vetorizer_lib.exceptions import ModelLoadError


class TextEmbedder:
    """Embedder for text using sentence-transformers models.

    Args:
        model_name: HuggingFace model identifier. Defaults to all-MiniLM-L6-v2.

    Raises:
        ModelLoadError: If the model cannot be loaded.

    Example:
        >>> embedder = TextEmbedder()
        >>> vectors = embedder.embed(["Hello world", "Another text"])
        >>> len(vectors[0])
        384
    """

    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self, model_name: str | None = None) -> None:
        """Initialize the text embedder with specified model."""
        self._model_name = model_name or self.DEFAULT_MODEL
        try:
            self._model = SentenceTransformer(self._model_name)
        except Exception as e:
            raise ModelLoadError(
                f"Cannot load model '{self._model_name}'. "
                "Check the model name on HuggingFace Hub.",
                cause=e,
            ) from e

    @property
    def dimension(self) -> int:
        """Return the dimension of embedding vectors.

        Returns:
            Integer dimension of the model's output vectors.
        """
        dim = self._model.get_sentence_embedding_dimension()
        if dim is None:
            return 384  # Default fallback
        return int(dim)

    @property
    def model_name(self) -> str:
        """Return the model name/identifier.

        Returns:
            String model name as provided or default.
        """
        return self._model_name

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts into vectors.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors, one per input text.

        Example:
            >>> embedder = TextEmbedder()
            >>> vectors = embedder.embed(["test"])
            >>> isinstance(vectors[0][0], float)
            True
        """
        if not texts:
            return []

        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return [vec.tolist() for vec in embeddings]

    def embed_image(self, image_paths: list[str]) -> list[list[float]]:
        """Embed images (not supported by text embedder).

        Args:
            image_paths: List of paths to image files.

        Raises:
            ModelLoadError: Always, as text embedder doesn't support images.
        """
        raise ModelLoadError(
            f"Model '{self._model_name}' does not support image embeddings. "
            "Use a CLIP-based model for image embeddings."
        )

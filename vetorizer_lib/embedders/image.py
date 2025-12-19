"""Image embedder using CLIP models.

This module provides the ImageEmbedder class for generating image embeddings
using HuggingFace CLIP models for multimodal search.
"""

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from vetorizer_lib.exceptions import IngestError, ModelLoadError


class ImageEmbedder:
    """Embedder for images and text using CLIP models.

    CLIP enables cross-modal search between text and images.

    Args:
        model_name: HuggingFace CLIP model identifier.

    Raises:
        ModelLoadError: If the model cannot be loaded.

    Example:
        >>> embedder = ImageEmbedder()
        >>> text_vectors = embedder.embed(["a photo of a cat"])
        >>> image_vectors = embedder.embed_image(["cat.jpg"])
    """

    DEFAULT_MODEL = "openai/clip-vit-base-patch32"

    def __init__(self, model_name: str | None = None, normalize: bool = True) -> None:
        """Initialize the image embedder with specified CLIP model.
        
        Args:
            model_name: HuggingFace CLIP model identifier. Uses default if None.
            normalize: Whether to normalize embeddings to unit length (L2 norm).
        """
        self._model_name = model_name or self.DEFAULT_MODEL
        self._normalize = normalize
        try:
            self._model = CLIPModel.from_pretrained(self._model_name)
            self._processor = CLIPProcessor.from_pretrained(self._model_name)
        except Exception as e:
            raise ModelLoadError(
                f"Cannot load CLIP model '{self._model_name}'. "
                "Check the model name on HuggingFace Hub.",
                cause=e,
            ) from e

    @property
    def dimension(self) -> int:
        """Return the dimension of embedding vectors.

        Returns:
            Integer dimension of the model's output vectors.
        """
        return int(self._model.config.projection_dim)

    @property
    def model_name(self) -> str:
        """Return the model name/identifier.

        Returns:
            String model name as provided or default.
        """
        return self._model_name

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts into vectors using CLIP.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors, one per input text.

        Example:
            >>> embedder = ImageEmbedder()
            >>> vectors = embedder.embed(["a red car"])
            >>> len(vectors[0])
            512
        """
        if not texts:
            return []

        inputs = self._processor(text=texts, return_tensors="pt", padding=True)

        with torch.no_grad():
            text_features = self._model.get_text_features(**inputs)
            # Normalize for cosine similarity if enabled
            if self._normalize:
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        return text_features.tolist()

    def embed_image(self, image_paths: list[str]) -> list[list[float]]:
        """Embed a list of images into vectors.

        Args:
            image_paths: List of paths to image files.

        Returns:
            List of embedding vectors, one per input image.

        Raises:
            IngestError: If an image cannot be loaded.

        Example:
            >>> embedder = ImageEmbedder()
            >>> vectors = embedder.embed_image(["photo.jpg"])
            >>> len(vectors[0])
            512
        """
        if not image_paths:
            return []

        images = []
        for path in image_paths:
            try:
                img = Image.open(path).convert("RGB")
                images.append(img)
            except Exception as e:
                raise IngestError(
                    f"Cannot load image '{path}'. Ensure the file exists and is a valid image.",
                    cause=e,
                ) from e

        inputs = self._processor(images=images, return_tensors="pt")

        with torch.no_grad():
            image_features = self._model.get_image_features(**inputs)
            # Normalize for cosine similarity if enabled
            if self._normalize:
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        return image_features.tolist()

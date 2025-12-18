from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IngestMode(str, Enum):
    """Mode for document ingestion and vector generation.
    
    Attributes:
        TEXT: Generate vectors from text content only.
        IMAGE: Generate vectors from image content only.
        HYBRID: Generate hybrid vectors from both text and image content.
    """
    TEXT = "text"
    IMAGE = "image"
    HYBRID = "hybrid"


@dataclass(frozen=True, slots=True)
class HybridVectorParts:
    text_vector: list[float]
    image_vector: list[float]


@dataclass(frozen=True, slots=True)
class HybridVectorComposition:
    order: tuple[str, str] = ("text", "image")


def normalize_vector(vector: list[float]) -> list[float]:
    """Normalize a vector to unit length (L2 norm = 1.0).
    
    Args:
        vector: Input vector to normalize.
        
    Returns:
        Normalized vector with L2 norm = 1.0.
        
    Raises:
        ValueError: If vector is empty or has zero norm.
        
    Example:
        >>> normalize_vector([3.0, 4.0])
        [0.6, 0.8]
    """
    if not vector:
        raise ValueError("vector must not be empty")
    
    # Calculate L2 norm
    norm = sum(x * x for x in vector) ** 0.5
    
    if norm == 0.0:
        raise ValueError("Cannot normalize zero vector")
    
    return [x / norm for x in vector]


def concat_hybrid_vector(
    parts: HybridVectorParts, 
    normalize_per_modality: bool = True
) -> list[float]:
    """Concatenate text and image vectors with optional per-modality normalization.
    
    Per-modality normalization ensures balanced contribution from both modalities.
    Without normalization, unnormalized text vectors (L2 norm: 3-8) can dominate
    normalized image vectors (L2 norm: 1.0), leading to 80/20 imbalance.

    Args:
        parts: Text and image vectors.
        normalize_per_modality: If True, normalize each modality independently
            before concatenation (recommended). If False, concatenate then normalize.

    Returns:
        Concatenated vector in the order: text then image.

    Raises:
        ValueError: If any vector is empty.

    Example:
        >>> concat_hybrid_vector(HybridVectorParts([3.0, 4.0], [1.0, 0.0]), True)
        [0.6, 0.8, 1.0, 0.0]  # Text normalized, image already normalized
    """
    if not parts.text_vector:
        raise ValueError("text_vector must not be empty")
    if not parts.image_vector:
        raise ValueError("image_vector must not be empty")

    if normalize_per_modality:
        # Normalize each modality independently (RECOMMENDED)
        text_norm = normalize_vector(parts.text_vector)
        image_norm = normalize_vector(parts.image_vector)
        return [*text_norm, *image_norm]
    else:
        # Concatenate then normalize globally
        concatenated = [*parts.text_vector, *parts.image_vector]
        return normalize_vector(concatenated)


def hybrid_composition_metadata(composition: HybridVectorComposition | None = None) -> dict[str, object]:
    if composition is None:
        composition = HybridVectorComposition()

    return {
        "hybrid_order": list(composition.order),
    }


def expected_hybrid_dimension(*, text_dimension: int, image_dimension: int) -> int:
    """Compute expected hybrid vector dimension.

    Args:
        text_dimension: Dimension of the text embedding.
        image_dimension: Dimension of the image embedding.

    Returns:
        Sum of text and image dimensions.

    Raises:
        ValueError: If any dimension is not positive.
    """
    if text_dimension <= 0:
        raise ValueError("text_dimension must be positive")
    if image_dimension <= 0:
        raise ValueError("image_dimension must be positive")

    return text_dimension + image_dimension


def validate_vector_dimension(*, vector: list[float], expected_dimension: int) -> None:
    """Validate that a vector has the expected dimension.

    Args:
        vector: Vector to validate.
        expected_dimension: Expected vector length.

    Raises:
        ValueError: If the vector length differs from expected_dimension.
    """
    if expected_dimension <= 0:
        raise ValueError("expected_dimension must be positive")

    actual = len(vector)
    if actual != expected_dimension:
        raise ValueError(f"Vector dimension mismatch: expected {expected_dimension}, got {actual}")

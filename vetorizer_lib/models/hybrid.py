from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HybridVectorParts:
    text_vector: list[float]
    image_vector: list[float]


@dataclass(frozen=True, slots=True)
class HybridVectorComposition:
    order: tuple[str, str] = ("text", "image")


def concat_hybrid_vector(parts: HybridVectorParts) -> list[float]:
    """Concatenate text and image vectors in a deterministic order.

    Args:
        parts: Text and image vectors.

    Returns:
        Concatenated vector in the order: text then image.

    Raises:
        ValueError: If any vector is empty.

    Example:
        >>> concat_hybrid_vector(HybridVectorParts([1.0, 2.0], [3.0]))
        [1.0, 2.0, 3.0]
    """
    if not parts.text_vector:
        raise ValueError("text_vector must not be empty")
    if not parts.image_vector:
        raise ValueError("image_vector must not be empty")

    return [*parts.text_vector, *parts.image_vector]


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

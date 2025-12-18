from __future__ import annotations

import pytest

from vetorizer_lib.models.hybrid import (
    HybridVectorParts,
    concat_hybrid_vector,
    expected_hybrid_dimension,
    hybrid_composition_metadata,
    validate_vector_dimension,
)


def test_concat_hybrid_vector_concatenates_in_text_then_image_order(
    sample_text_vector: list[float],
    sample_image_vector: list[float],
) -> None:
    # Test without normalization to verify concatenation order
    result = concat_hybrid_vector(
        HybridVectorParts(text_vector=sample_text_vector, image_vector=sample_image_vector),
        normalize=False
    )

    assert result == [*sample_text_vector, *sample_image_vector]


def test_concat_hybrid_vector_raises_for_empty_text_vector(sample_image_vector: list[float]) -> None:
    with pytest.raises(ValueError, match="text_vector must not be empty"):
        concat_hybrid_vector(HybridVectorParts(text_vector=[], image_vector=sample_image_vector))


def test_concat_hybrid_vector_raises_for_empty_image_vector(sample_text_vector: list[float]) -> None:
    with pytest.raises(ValueError, match="image_vector must not be empty"):
        concat_hybrid_vector(HybridVectorParts(text_vector=sample_text_vector, image_vector=[]))


def test_expected_hybrid_dimension_sums_dimensions() -> None:
    assert expected_hybrid_dimension(text_dimension=3, image_dimension=5) == 8


@pytest.mark.parametrize("text_dimension", [0, -1])
def test_expected_hybrid_dimension_raises_for_non_positive_text_dimension(text_dimension: int) -> None:
    with pytest.raises(ValueError, match="text_dimension must be positive"):
        expected_hybrid_dimension(text_dimension=text_dimension, image_dimension=5)


@pytest.mark.parametrize("image_dimension", [0, -1])
def test_expected_hybrid_dimension_raises_for_non_positive_image_dimension(image_dimension: int) -> None:
    with pytest.raises(ValueError, match="image_dimension must be positive"):
        expected_hybrid_dimension(text_dimension=3, image_dimension=image_dimension)


def test_validate_vector_dimension_accepts_matching_dimension(sample_text_vector: list[float]) -> None:
    validate_vector_dimension(vector=sample_text_vector, expected_dimension=len(sample_text_vector))


def test_validate_vector_dimension_raises_for_non_positive_expected_dimension(
    sample_text_vector: list[float],
) -> None:
    with pytest.raises(ValueError, match="expected_dimension must be positive"):
        validate_vector_dimension(vector=sample_text_vector, expected_dimension=0)


def test_validate_vector_dimension_raises_for_mismatch(sample_text_vector: list[float]) -> None:
    with pytest.raises(ValueError, match=r"Vector dimension mismatch: expected 999, got 3"):
        validate_vector_dimension(vector=sample_text_vector, expected_dimension=999)


def test_hybrid_composition_metadata_defaults_to_text_image_order() -> None:
    assert hybrid_composition_metadata() == {"hybrid_order": ["text", "image"]}

"""Shared pytest fixtures for vetorizer_lib tests.

This module provides common fixtures used across unit, integration, and contract tests.
"""

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_embedder() -> MagicMock:
    """Create a mock embedder that returns deterministic vectors.

    Returns:
        MagicMock configured to return 384-dimensional vectors.

    Example:
        >>> def test_with_mock(mock_embedder):
        ...     result = mock_embedder.embed(["test"])
        ...     assert len(result[0]) == 384
    """
    embedder = MagicMock()
    embedder.embed.return_value = [[0.1] * 384]
    embedder.dimension = 384
    return embedder


@pytest.fixture
def mock_store() -> MagicMock:
    """Create a mock vector store for testing.

    Returns:
        MagicMock configured with upsert and search methods.

    Example:
        >>> def test_with_mock(mock_store):
        ...     mock_store.upsert([document])
        ...     mock_store.upsert.assert_called_once()
    """
    store = MagicMock()
    store.upsert.return_value = None
    store.search.return_value = []
    return store


@pytest.fixture
def sample_csv_content() -> str:
    """Sample CSV content for testing ingestion.

    Returns:
        CSV string with id, title, and description columns.
    """
    return """id,title,description
1,Product A,A great product for testing
2,Product B,Another excellent product
3,Product C,The best product ever"""


@pytest.fixture
def sample_csv_file(tmp_path: Any, sample_csv_content: str) -> Generator[str, None, None]:
    """Create a temporary CSV file for testing.

    Args:
        tmp_path: pytest tmp_path fixture.
        sample_csv_content: CSV content to write.

    Yields:
        Path to the temporary CSV file.
    """
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(sample_csv_content)
    yield str(csv_file)


@pytest.fixture
def empty_csv_file(tmp_path: Any) -> Generator[str, None, None]:
    """Create an empty CSV file for testing edge cases.

    Args:
        tmp_path: pytest tmp_path fixture.

    Yields:
        Path to the empty CSV file.
    """
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("id,title,description\n")
    yield str(csv_file)


@pytest.fixture
def sample_text_vector() -> list[float]:
    """Sample text vector for hybrid tests.

    Returns:
        A small deterministic vector.
    """
    return [1.0, 2.0, 3.0]


@pytest.fixture
def sample_image_vector() -> list[float]:
    """Sample image vector for hybrid tests.

    Returns:
        A small deterministic vector.
    """
    return [4.0, 5.0]


@pytest.fixture
def sample_image_file(tmp_path: Any) -> Generator[str, None, None]:
    """Create a temporary image file for tests.

    Args:
        tmp_path: pytest tmp_path fixture.

    Yields:
        Path to a temporary PNG file.
    """
    image_file = tmp_path / "sample.png"
    image_file.write_bytes(b"\x89PNG\r\n\x1a\n")
    yield str(image_file)

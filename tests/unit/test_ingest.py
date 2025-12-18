"""Unit tests for CSV ingestion.

Tests for CSV parsing and document creation with mocked embedder/store.
"""

import pytest

from vetorizer_lib.models.config import IngestConfig
from vetorizer_lib.models.document import ContentType, Document


class TestIngestConfig:
    """Tests for IngestConfig validation."""

    def test_config_requires_file_path(self) -> None:
        """IngestConfig requires file_path."""
        config = IngestConfig(file_path="test.csv", content_column="text")
        assert config.file_path == "test.csv"

    def test_config_requires_content_column(self) -> None:
        """IngestConfig requires content_column."""
        config = IngestConfig(file_path="test.csv", content_column="description")
        assert config.content_column == "description"

    def test_config_default_batch_size(self) -> None:
        """IngestConfig has default batch_size of 100."""
        config = IngestConfig(file_path="test.csv", content_column="text")
        assert config.batch_size == 100

    def test_config_custom_batch_size(self) -> None:
        """IngestConfig accepts custom batch_size."""
        config = IngestConfig(file_path="test.csv", content_column="text", batch_size=50)
        assert config.batch_size == 50


class TestCSVParsing:
    """Tests for CSV file parsing."""

    def test_read_csv_creates_documents(self, sample_csv_file: str) -> None:
        """CSV reader creates Document objects from rows."""
        from vetorizer_lib.ingest.csv import read_csv_batches

        config = IngestConfig(
            file_path=sample_csv_file,
            content_column="description",
            id_column="id",
        )
        
        batches = list(read_csv_batches(config))
        assert len(batches) > 0
        
        all_docs = [doc for batch in batches for doc in batch]
        assert len(all_docs) == 3
        assert all_docs[0].id == "1"
        assert "great product" in all_docs[0].content.lower()

    def test_read_csv_with_metadata_columns(self, sample_csv_file: str) -> None:
        """CSV reader includes metadata columns in documents."""
        from vetorizer_lib.ingest.csv import read_csv_batches

        config = IngestConfig(
            file_path=sample_csv_file,
            content_column="description",
            id_column="id",
            metadata_columns=["title"],
        )
        
        batches = list(read_csv_batches(config))
        all_docs = [doc for batch in batches for doc in batch]
        
        assert "title" in all_docs[0].metadata
        assert all_docs[0].metadata["title"] == "Product A"

    def test_read_csv_generates_ids_when_no_id_column(self, sample_csv_file: str) -> None:
        """CSV reader generates UUIDs when id_column is None."""
        from vetorizer_lib.ingest.csv import read_csv_batches

        config = IngestConfig(
            file_path=sample_csv_file,
            content_column="description",
        )
        
        batches = list(read_csv_batches(config))
        all_docs = [doc for batch in batches for doc in batch]
        
        # All IDs should be unique
        ids = [doc.id for doc in all_docs]
        assert len(ids) == len(set(ids))

    def test_read_csv_respects_batch_size(self, sample_csv_file: str) -> None:
        """CSV reader yields batches of specified size."""
        from vetorizer_lib.ingest.csv import read_csv_batches

        config = IngestConfig(
            file_path=sample_csv_file,
            content_column="description",
            batch_size=2,
        )
        
        batches = list(read_csv_batches(config))
        # With 3 rows and batch_size=2, should get 2 batches
        assert len(batches) == 2
        assert len(batches[0]) == 2
        assert len(batches[1]) == 1

    def test_read_csv_skips_empty_content(self, tmp_path: str) -> None:
        """CSV reader skips rows with empty content when skip_empty=True."""
        from vetorizer_lib.ingest.csv import read_csv_batches
        import pathlib

        csv_content = """id,description
1,Valid content
2,
3,Another valid"""
        csv_file = pathlib.Path(tmp_path) / "with_empty.csv"
        csv_file.write_text(csv_content)

        config = IngestConfig(
            file_path=str(csv_file),
            content_column="description",
            id_column="id",
            skip_empty=True,
        )
        
        batches = list(read_csv_batches(config))
        all_docs = [doc for batch in batches for doc in batch]
        
        assert len(all_docs) == 2
        assert all_docs[0].id == "1"
        assert all_docs[1].id == "3"

    def test_read_csv_includes_empty_when_skip_empty_false(self, tmp_path: str) -> None:
        """CSV reader includes empty rows when skip_empty=False."""
        from vetorizer_lib.ingest.csv import read_csv_batches
        import pathlib

        csv_content = """id,description
1,Valid content
2,
3,Another valid"""
        csv_file = pathlib.Path(tmp_path) / "with_empty.csv"
        csv_file.write_text(csv_content)

        config = IngestConfig(
            file_path=str(csv_file),
            content_column="description",
            id_column="id",
            skip_empty=False,
        )
        
        batches = list(read_csv_batches(config))
        all_docs = [doc for batch in batches for doc in batch]
        
        assert len(all_docs) == 3

    def test_read_csv_raises_on_missing_file(self) -> None:
        """CSV reader raises IngestError for missing file."""
        from vetorizer_lib.ingest.csv import read_csv_batches
        from vetorizer_lib.exceptions import IngestError

        config = IngestConfig(
            file_path="nonexistent.csv",
            content_column="description",
        )
        
        with pytest.raises(IngestError):
            list(read_csv_batches(config))

    def test_read_csv_raises_on_missing_column(self, sample_csv_file: str) -> None:
        """CSV reader raises ConfigurationError for missing column."""
        from vetorizer_lib.ingest.csv import read_csv_batches
        from vetorizer_lib.exceptions import ConfigurationError

        config = IngestConfig(
            file_path=sample_csv_file,
            content_column="nonexistent_column",
        )
        
        with pytest.raises(ConfigurationError):
            list(read_csv_batches(config))

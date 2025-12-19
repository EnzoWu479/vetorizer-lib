"""Unit tests for text-only ingestion mode."""

import pytest
from pathlib import Path

from vetorizer_lib.models.hybrid import IngestMode
from vetorizer_lib.ingest.csv import read_csv_batches
from vetorizer_lib.models.config import IngestConfig
from vetorizer_lib.models.document import ContentType


def test_text_only_ingestion_basic(tmp_path: Path):
    """Test basic text-only ingestion from CSV."""
    # Create test CSV with text and label
    csv_file = tmp_path / "text_dataset.csv"
    csv_file.write_text("text,label\nHello world,greeting\nGoodbye,farewell\n")
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.TEXT))
    
    assert len(batches) == 1, "Should have one batch"
    assert len(batches[0]) == 2, "Should have 2 documents"
    assert batches[0][0].content == "Hello world"
    assert batches[0][1].content == "Goodbye"


def test_text_only_ingestion_with_metadata(tmp_path: Path):
    """Test text ingestion with additional metadata columns."""
    csv_file = tmp_path / "text_metadata.csv"
    csv_file.write_text(
        "text,label,category,author\n"
        "Hello,greeting,social,alice\n"
        "Python is great,statement,tech,bob\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        metadata_columns=["category", "author"],
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.TEXT))
    doc = batches[0][0]
    
    assert doc.content == "Hello"
    assert doc.metadata["category"] == "social"
    assert doc.metadata["author"] == "alice"


def test_text_only_ingestion_with_id_column(tmp_path: Path):
    """Test text ingestion with custom ID column."""
    csv_file = tmp_path / "text_with_ids.csv"
    csv_file.write_text(
        "id,text,label\n"
        "doc-001,Hello world,greeting\n"
        "doc-002,Goodbye,farewell\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        id_column="id",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.TEXT))
    
    assert batches[0][0].id == "doc-001"
    assert batches[0][1].id == "doc-002"


def test_text_only_ingestion_empty_text_rows_skipped(tmp_path: Path):
    """Test that rows with empty text content are skipped."""
    csv_file = tmp_path / "text_with_empty.csv"
    csv_file.write_text(
        "text,label\n"
        "Valid text,greeting\n"
        ",missing\n"
        "   ,whitespace\n"
        "Another valid,statement\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.TEXT))
    docs = batches[0]
    
    # Should skip rows with empty or whitespace-only text
    assert len(docs) == 2
    assert docs[0].content == "Valid text"
    assert docs[1].content == "Another valid"


def test_text_only_ingestion_batching(tmp_path: Path):
    """Test that batching works correctly for text ingestion."""
    csv_file = tmp_path / "text_large.csv"
    lines = ["text,label\n"]
    for i in range(25):
        lines.append(f"Text {i},label{i}\n")
    csv_file.write_text("".join(lines))
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.TEXT))
    
    assert len(batches) == 3, "Should have 3 batches (10, 10, 5)"
    assert len(batches[0]) == 10
    assert len(batches[1]) == 10
    assert len(batches[2]) == 5


def test_text_only_ingestion_missing_column_error(tmp_path: Path):
    """Test error when required text column is missing."""
    csv_file = tmp_path / "missing_column.csv"
    csv_file.write_text("wrong_column,label\nHello,greeting\n")
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",  # This column doesn't exist
        batch_size=10,
    )
    
    with pytest.raises(Exception):  # Should raise ConfigurationError or similar
        list(read_csv_batches(config, content_type=ContentType.TEXT))

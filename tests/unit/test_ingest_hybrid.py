"""Unit tests for hybrid ingestion mode (text + image)."""

import pytest
from pathlib import Path
from PIL import Image

from vetorizer_lib.models.hybrid import IngestMode
from vetorizer_lib.ingest.csv import read_csv_batches
from vetorizer_lib.models.config import IngestConfig
from vetorizer_lib.models.document import ContentType


@pytest.fixture
def test_documents(tmp_path: Path) -> tuple[Path, Path]:
    """Create test documents directory with images and a CSV."""
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    
    images_dir = docs_dir / "images"
    images_dir.mkdir()
    
    # Create test images
    for i in range(3):
        img = Image.new("RGB", (100, 100), color=(i * 80, i * 80, i * 80))
        img.save(images_dir / f"doc_{i}.jpg")
    
    return docs_dir, images_dir


def test_hybrid_ingestion_basic(tmp_path: Path, test_documents: tuple[Path, Path]):
    """Test basic hybrid ingestion with text and image columns."""
    docs_dir, images_dir = test_documents
    
    csv_file = tmp_path / "hybrid_dataset.csv"
    csv_file.write_text(
        f"text,image_path,label\n"
        f"Cat description,{images_dir}/doc_0.jpg,cat\n"
        f"Dog description,{images_dir}/doc_1.jpg,dog\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        image_column="image_path",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.HYBRID))
    
    assert len(batches) == 1
    assert len(batches[0]) == 2
    
    doc = batches[0][0]
    assert doc.content == "Cat description"
    assert "doc_0.jpg" in doc.metadata.get("image_path", "")


def test_hybrid_ingestion_with_metadata(tmp_path: Path, test_documents: tuple[Path, Path]):
    """Test hybrid ingestion with additional metadata columns."""
    docs_dir, images_dir = test_documents
    
    csv_file = tmp_path / "hybrid_metadata.csv"
    csv_file.write_text(
        f"text,image_path,label,category,author\n"
        f"Cat info,{images_dir}/doc_0.jpg,animal,mammals,alice\n"
        f"Dog info,{images_dir}/doc_1.jpg,animal,mammals,bob\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        image_column="image_path",
        metadata_columns=["category", "author"],
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.HYBRID))
    doc = batches[0][0]
    
    assert doc.content == "Cat info"
    assert doc.metadata["category"] == "mammals"
    assert doc.metadata["author"] == "alice"
    assert "doc_0.jpg" in doc.metadata["image_path"]


def test_hybrid_ingestion_missing_text_skipped(tmp_path: Path, test_documents: tuple[Path, Path]):
    """Test that rows with missing text are skipped in hybrid mode."""
    docs_dir, images_dir = test_documents
    
    csv_file = tmp_path / "hybrid_missing_text.csv"
    csv_file.write_text(
        f"text,image_path,label\n"
        f"Valid text,{images_dir}/doc_0.jpg,ok\n"
        f",{images_dir}/doc_1.jpg,missing_text\n"
        f"Another valid,{images_dir}/doc_2.jpg,ok\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        image_column="image_path",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.HYBRID))
    docs = batches[0]
    
    # Should skip row with missing text
    assert len(docs) == 2
    assert docs[0].content == "Valid text"
    assert docs[1].content == "Another valid"


def test_hybrid_ingestion_missing_image_skipped(tmp_path: Path, test_documents: tuple[Path, Path]):
    """Test that rows with missing image files are skipped in hybrid mode."""
    docs_dir, images_dir = test_documents
    
    csv_file = tmp_path / "hybrid_missing_image.csv"
    csv_file.write_text(
        f"text,image_path,label\n"
        f"Text with image,{images_dir}/doc_0.jpg,ok\n"
        f"Text without image,{images_dir}/nonexistent.jpg,missing_img\n"
        f"Another with image,{images_dir}/doc_1.jpg,ok\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        image_column="image_path",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.HYBRID))
    docs = batches[0]
    
    # Should skip row with nonexistent image
    assert len(docs) == 2
    assert docs[0].content == "Text with image"
    assert docs[1].content == "Another with image"


def test_hybrid_ingestion_corrupted_image_skipped(tmp_path: Path):
    """Test that rows with corrupted images are skipped in hybrid mode."""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    
    # Create valid image
    img = Image.new("RGB", (100, 100))
    img.save(images_dir / "valid.jpg")
    
    # Create corrupted "image"
    (images_dir / "corrupted.jpg").write_text("not an image file")
    
    csv_file = tmp_path / "hybrid_corrupted.csv"
    csv_file.write_text(
        f"text,image_path,label\n"
        f"Valid doc,{images_dir}/valid.jpg,ok\n"
        f"Corrupted doc,{images_dir}/corrupted.jpg,bad\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        image_column="image_path",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.HYBRID))
    docs = batches[0]
    
    # Should skip row with corrupted image
    assert len(docs) == 1
    assert docs[0].content == "Valid doc"


def test_hybrid_ingestion_both_missing_skipped(tmp_path: Path):
    """Test that rows with both text and image missing are skipped."""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    
    img = Image.new("RGB", (100, 100))
    img.save(images_dir / "valid.jpg")
    
    csv_file = tmp_path / "hybrid_both_missing.csv"
    csv_file.write_text(
        f"text,image_path,label\n"
        f"Valid text,{images_dir}/valid.jpg,ok\n"
        f",{images_dir}/valid.jpg,missing_text\n"
        f"Valid text,{images_dir}/nonexistent.jpg,missing_image\n"
        f",,both_missing\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        image_column="image_path",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.HYBRID))
    docs = batches[0]
    
    # Only first row should be kept
    assert len(docs) == 1
    assert docs[0].content == "Valid text"


def test_hybrid_ingestion_batching(tmp_path: Path):
    """Test that batching works correctly for hybrid ingestion."""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    
    # Create 25 test images
    for i in range(25):
        img = Image.new("RGB", (50, 50))
        img.save(images_dir / f"img_{i}.jpg")
    
    csv_file = tmp_path / "hybrid_large.csv"
    lines = ["text,image_path,label\n"]
    for i in range(25):
        lines.append(f"Text {i},{images_dir}/img_{i}.jpg,label{i}\n")
    csv_file.write_text("".join(lines))
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        image_column="image_path",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.HYBRID))
    
    assert len(batches) == 3, "Should have 3 batches (10, 10, 5)"
    assert len(batches[0]) == 10
    assert len(batches[1]) == 10
    assert len(batches[2]) == 5


def test_hybrid_ingestion_missing_columns_error(tmp_path: Path):
    """Test error when required columns are missing in hybrid mode."""
    csv_file = tmp_path / "hybrid_missing_columns.csv"
    csv_file.write_text("text,label\nHello,greeting\n")  # Missing image_path column
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="text",
        image_column="image_path",  # This column doesn't exist
        batch_size=10,
    )
    
    with pytest.raises(Exception):  # Should raise ConfigurationError
        list(read_csv_batches(config, content_type=ContentType.HYBRID))

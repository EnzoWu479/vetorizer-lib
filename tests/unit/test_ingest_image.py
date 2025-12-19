"""Unit tests for image-only ingestion mode."""

import pytest
from pathlib import Path
from PIL import Image

from vetorizer_lib.models.hybrid import IngestMode
from vetorizer_lib.ingest.csv import read_csv_batches
from vetorizer_lib.models.config import IngestConfig
from vetorizer_lib.models.document import ContentType


@pytest.fixture
def test_images(tmp_path: Path) -> Path:
    """Create test images directory with sample images."""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    
    # Create RGB test images
    for i in range(3):
        img = Image.new("RGB", (100, 100), color=(i * 50, i * 50, i * 50))
        img.save(images_dir / f"test_{i}.jpg")
    
    return images_dir


def test_image_only_ingestion_basic(tmp_path: Path, test_images: Path):
    """Test basic image-only ingestion from CSV."""
    csv_file = tmp_path / "image_dataset.csv"
    csv_file.write_text(
        f"image_path,label\n"
        f"{test_images}/test_0.jpg,cat\n"
        f"{test_images}/test_1.jpg,dog\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="image_path",
        image_column="image_path",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.IMAGE))
    
    assert len(batches) == 1
    assert len(batches[0]) == 2
    assert Path(batches[0][0].content).name == "test_0.jpg"
    assert Path(batches[0][1].content).name == "test_1.jpg"


def test_image_only_ingestion_with_metadata(tmp_path: Path, test_images: Path):
    """Test image ingestion with metadata columns."""
    csv_file = tmp_path / "image_metadata.csv"
    csv_file.write_text(
        f"image_path,label,category,source\n"
        f"{test_images}/test_0.jpg,cat,animal,dataset_a\n"
        f"{test_images}/test_1.jpg,dog,animal,dataset_b\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="image_path",
        image_column="image_path",
        metadata_columns=["category", "source"],
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.IMAGE))
    doc = batches[0][0]
    
    assert doc.metadata["category"] == "animal"
    assert doc.metadata["source"] == "dataset_a"


def test_image_only_ingestion_missing_file_skipped(tmp_path: Path, test_images: Path):
    """Test that rows with missing image files are skipped."""
    csv_file = tmp_path / "image_missing.csv"
    csv_file.write_text(
        f"image_path,label\n"
        f"{test_images}/test_0.jpg,cat\n"
        f"{test_images}/nonexistent.jpg,missing\n"
        f"{test_images}/test_1.jpg,dog\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="image_path",
        image_column="image_path",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.IMAGE))
    docs = batches[0]
    
    # Should skip row with nonexistent file
    assert len(docs) == 2
    assert "test_0.jpg" in docs[0].content
    assert "test_1.jpg" in docs[1].content


def test_image_only_ingestion_invalid_format_skipped(tmp_path: Path):
    """Test that rows with invalid image formats are skipped."""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    
    # Create valid image
    img = Image.new("RGB", (100, 100))
    img.save(images_dir / "valid.jpg")
    
    # Create invalid "image" (text file)
    (images_dir / "invalid.jpg").write_text("not an image")
    
    csv_file = tmp_path / "image_invalid.csv"
    csv_file.write_text(
        f"image_path,label\n"
        f"{images_dir}/valid.jpg,ok\n"
        f"{images_dir}/invalid.jpg,bad\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="image_path",
        image_column="image_path",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.IMAGE))
    docs = batches[0]
    
    # Should skip corrupted image
    assert len(docs) == 1
    assert "valid.jpg" in docs[0].content


def test_image_only_ingestion_relative_paths(tmp_path: Path, test_images: Path):
    """Test image ingestion with relative paths."""
    csv_file = tmp_path / "image_relative.csv"
    
    # Write CSV with relative paths
    csv_file.write_text(
        "image_path,label\n"
        "images/test_0.jpg,cat\n"
        "images/test_1.jpg,dog\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="image_path",
        image_column="image_path",
        batch_size=10,
        base_path=str(tmp_path),  # Base path for resolving relative paths
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.IMAGE))
    
    assert len(batches[0]) == 2


def test_image_only_ingestion_batching(tmp_path: Path):
    """Test that batching works correctly for image ingestion."""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    
    # Create 25 test images
    for i in range(25):
        img = Image.new("RGB", (50, 50))
        img.save(images_dir / f"img_{i}.jpg")
    
    csv_file = tmp_path / "image_large.csv"
    lines = ["image_path,label\n"]
    for i in range(25):
        lines.append(f"{images_dir}/img_{i}.jpg,label{i}\n")
    csv_file.write_text("".join(lines))
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="image_path",
        image_column="image_path",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.IMAGE))
    
    assert len(batches) == 3, "Should have 3 batches (10, 10, 5)"
    assert len(batches[0]) == 10
    assert len(batches[1]) == 10
    assert len(batches[2]) == 5


def test_image_only_ingestion_empty_path_skipped(tmp_path: Path):
    """Test that rows with empty image paths are skipped."""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    img = Image.new("RGB", (100, 100))
    img.save(images_dir / "valid.jpg")
    
    csv_file = tmp_path / "image_empty_paths.csv"
    csv_file.write_text(
        f"image_path,label\n"
        f"{images_dir}/valid.jpg,ok\n"
        f",empty\n"
        f"   ,whitespace\n"
    )
    
    config = IngestConfig(
        file_path=str(csv_file),
        content_column="image_path",
        image_column="image_path",
        batch_size=10,
    )
    
    batches = list(read_csv_batches(config, content_type=ContentType.IMAGE))
    docs = batches[0]
    
    assert len(docs) == 1
    assert "valid.jpg" in docs[0].content

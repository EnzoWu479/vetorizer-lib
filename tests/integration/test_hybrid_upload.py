"""Integration tests for hybrid dataset ingestion.

Tests for end-to-end hybrid ingestion with text, image, and hybrid modes.
"""

import pytest
from pathlib import Path
import tempfile
import csv
from PIL import Image
import io

from vetorizer_lib.models.config import IngestConfig
from vetorizer_lib.models.document import ContentType
from vetorizer_lib.ingest.csv import read_csv_batches


class TestHybridDatasetIngestion:
    """Integration tests for mixed dataset ingestion (T044)."""

    @pytest.fixture
    def test_images(self, tmp_path: Path) -> dict[str, Path]:
        """Create test images for ingestion."""
        images = {}
        
        # Create 3 test images with different sizes
        for i, size in enumerate([(100, 100), (200, 150), (150, 200)], 1):
            img = Image.new('RGB', size, color=(i * 50, 100, 200 - i * 30))
            img_path = tmp_path / f"test_image_{i}.png"
            img.save(img_path)
            images[f"image{i}"] = img_path
        
        return images

    @pytest.fixture
    def mixed_csv(self, tmp_path: Path, test_images: dict[str, Path]) -> Path:
        """Create a mixed CSV with text, image, and hybrid entries."""
        csv_file = tmp_path / "mixed_dataset.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'text', 'image_path', 'category', 'title'])
            
            # Text-only entries (no image)
            writer.writerow(['1', 'First text document', '', 'news', 'Article 1'])
            writer.writerow(['2', 'Second text document', '', 'news', 'Article 2'])
            
            # Image-only entries (no text)
            writer.writerow(['3', '', str(test_images['image1']), 'photo', 'Landscape 1'])
            writer.writerow(['4', '', str(test_images['image2']), 'photo', 'Portrait 1'])
            
            # Hybrid entries (both text and image)
            writer.writerow(['5', 'Text with image 1', str(test_images['image1']), 'article', 'Illustrated 1'])
            writer.writerow(['6', 'Text with image 2', str(test_images['image2']), 'article', 'Illustrated 2'])
            writer.writerow(['7', 'Text with image 3', str(test_images['image3']), 'blog', 'Post 1'])
        
        return csv_file

    def test_text_only_ingestion(self, mixed_csv: Path) -> None:
        """Ingest dataset as text-only mode, skipping rows without text."""
        config = IngestConfig(
            file_path=str(mixed_csv),
            content_column='text',
            id_column='id',
            metadata_columns=['category', 'title'],
            skip_empty=True,
            batch_size=10,
        )
        
        # Flatten batches into single list of documents
        batches = list(read_csv_batches(config, content_type=ContentType.TEXT))
        docs = [doc for batch in batches for doc in batch]
        
        # Should only get text entries (rows 1, 2) and hybrid entries (rows 5, 6, 7)
        assert len(docs) == 5
        assert all(doc.content for doc in docs)
        assert all(doc.content_type == ContentType.TEXT for doc in docs)
        assert docs[0].id == '1'
        assert docs[1].id == '2'
        assert docs[2].id == '5'

    def test_image_only_ingestion(self, mixed_csv: Path, tmp_path: Path) -> None:
        """Ingest dataset as image-only mode, skipping rows without images."""
        config = IngestConfig(
            file_path=str(mixed_csv),
            content_column='image_path',
            image_column='image_path',
            id_column='id',
            metadata_columns=['category', 'title'],
            skip_empty=True,
            batch_size=10,
            base_path=str(tmp_path),
        )
        
        # Flatten batches into single list of documents
        batches = list(read_csv_batches(config, content_type=ContentType.IMAGE))
        docs = [doc for batch in batches for doc in batch]
        
        # Should only get image entries (rows 3, 4) and hybrid entries (rows 5, 6, 7)
        assert len(docs) == 5
        assert all(doc.content for doc in docs)  # content should be image path
        assert all(doc.content_type == ContentType.IMAGE for doc in docs)
        assert docs[0].id == '3'
        assert docs[1].id == '4'
        assert docs[2].id == '5'

    def test_hybrid_mode_ingestion(self, mixed_csv: Path, tmp_path: Path) -> None:
        """Ingest dataset as hybrid mode, requiring both text and image."""
        config = IngestConfig(
            file_path=str(mixed_csv),
            content_column='text',
            image_column='image_path',
            id_column='id',
            metadata_columns=['category', 'title'],
            skip_empty=True,
            batch_size=10,
            base_path=str(tmp_path),
        )
        
        # Flatten batches into single list of documents
        batches = list(read_csv_batches(config, content_type=ContentType.HYBRID))
        docs = [doc for batch in batches for doc in batch]
        
        # Should only get hybrid entries (rows 5, 6, 7) - rows with both text and image
        assert len(docs) == 3
        assert all(doc.content for doc in docs)
        assert all(doc.content_type == ContentType.HYBRID for doc in docs)
        assert all('image_path' in doc.metadata for doc in docs)
        assert docs[0].id == '5'
        assert docs[1].id == '6'
        assert docs[2].id == '7'

    def test_mixed_ingestion_preserves_metadata(self, mixed_csv: Path, tmp_path: Path) -> None:
        """Verify metadata is preserved across all ingestion modes."""
        # Test with hybrid mode
        config = IngestConfig(
            file_path=str(mixed_csv),
            content_column='text',
            image_column='image_path',
            id_column='id',
            metadata_columns=['category', 'title'],
            skip_empty=True,
            batch_size=10,
            base_path=str(tmp_path),
        )
        
        # Flatten batches into single list of documents
        batches = list(read_csv_batches(config, content_type=ContentType.HYBRID))
        docs = [doc for batch in batches for doc in batch]
        
        # Verify metadata from first hybrid entry
        assert docs[0].metadata['category'] == 'article'
        assert docs[0].metadata['title'] == 'Illustrated 1'
        assert 'image_path' in docs[0].metadata

    def test_mixed_ingestion_with_missing_files(self, tmp_path: Path) -> None:
        """Handle mixed dataset with some missing image files gracefully."""
        # Create CSV with missing image reference
        csv_file = tmp_path / "mixed_missing.csv"
        
        # Create one valid image
        img = Image.new('RGB', (100, 100), color=(100, 100, 100))
        valid_img = tmp_path / "valid.png"
        img.save(valid_img)
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'text', 'image_path'])
            writer.writerow(['1', 'Text with valid image', str(valid_img)])
            writer.writerow(['2', 'Text with missing image', '/nonexistent/missing.png'])
            writer.writerow(['3', 'Text only', ''])
        
        config = IngestConfig(
            file_path=str(csv_file),
            content_column='text',
            image_column='image_path',
            id_column='id',
            skip_empty=True,
            batch_size=10,
            base_path=str(tmp_path),
        )
        
        # Flatten batches into single list of documents
        batches = list(read_csv_batches(config, content_type=ContentType.HYBRID))
        docs = [doc for batch in batches for doc in batch]
        
        # Should only get row 1 (valid text + valid image)
        assert len(docs) == 1
        assert docs[0].id == '1'

    def test_mixed_ingestion_batching(self, tmp_path: Path) -> None:
        """Verify batching works correctly with mixed dataset."""
        # Create multiple test images
        images = []
        for i in range(10):
            img = Image.new('RGB', (100, 100), color=(i * 25, 100, 200))
            img_path = tmp_path / f"batch_img_{i}.png"
            img.save(img_path)
            images.append(img_path)
        
        # Create CSV with 10 hybrid entries
        csv_file = tmp_path / "batch_dataset.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'text', 'image_path'])
            for i in range(10):
                writer.writerow([str(i), f'Text {i}', str(images[i])])
        
        config = IngestConfig(
            file_path=str(csv_file),
            content_column='text',
            image_column='image_path',
            id_column='id',
            skip_empty=False,
            batch_size=3,  # Small batch size to test batching
            base_path=str(tmp_path),
        )
        
        batches = list(read_csv_batches(config, content_type=ContentType.HYBRID))
        docs = [doc for batch in batches for doc in batch]
        
        # Should get all 10 documents (batches should have batch_size=3)
        assert len(docs) == 10
        assert all(doc.content_type == ContentType.HYBRID for doc in docs)
        # Verify we actually got 4 batches (3+3+3+1)
        assert len(batches) == 4

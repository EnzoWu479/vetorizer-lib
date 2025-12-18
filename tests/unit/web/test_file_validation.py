"""Unit tests for file validation service."""

import io
import pytest
from vetorizer_lib.web.services.validation_service import (
    validate_file_extension,
    validate_file_size,
    validate_single_file,
    validate_file_batch,
    MAX_FILE_SIZE_BYTES,
    MAX_BATCH_FILES,
)
from vetorizer_lib.web.models.schemas import IngestMode, ValidationStatus


class TestFileExtensionValidation:
    """Test file extension validation."""
    
    def test_valid_csv_for_text_mode(self):
        """Test CSV file is valid for text mode."""
        is_valid, error = validate_file_extension("data.csv", IngestMode.TEXT)
        
        assert is_valid is True
        assert error is None
    
    def test_valid_txt_for_text_mode(self):
        """Test TXT file is valid for text mode."""
        is_valid, error = validate_file_extension("document.txt", IngestMode.TEXT)
        
        assert is_valid is True
        assert error is None
    
    def test_invalid_jpg_for_text_mode(self):
        """Test JPG file is invalid for text mode."""
        is_valid, error = validate_file_extension("image.jpg", IngestMode.TEXT)
        
        assert is_valid is False
        assert "not allowed" in error.lower()
        assert ".csv" in error
    
    def test_valid_jpg_for_image_mode(self):
        """Test JPG file is valid for image mode."""
        is_valid, error = validate_file_extension("photo.jpg", IngestMode.IMAGE)
        
        assert is_valid is True
        assert error is None
    
    def test_valid_png_for_image_mode(self):
        """Test PNG file is valid for image mode."""
        is_valid, error = validate_file_extension("screenshot.png", IngestMode.IMAGE)
        
        assert is_valid is True
        assert error is None
    
    def test_invalid_csv_for_image_mode(self):
        """Test CSV file is invalid for image mode."""
        is_valid, error = validate_file_extension("data.csv", IngestMode.IMAGE)
        
        assert is_valid is False
        assert "not allowed" in error.lower()
    
    def test_valid_csv_for_hybrid_mode(self):
        """Test CSV file is valid for hybrid mode."""
        is_valid, error = validate_file_extension("mixed.csv", IngestMode.HYBRID)
        
        assert is_valid is True
        assert error is None
    
    def test_case_insensitive_extension(self):
        """Test extensions are case-insensitive."""
        is_valid, error = validate_file_extension("data.CSV", IngestMode.TEXT)
        
        assert is_valid is True


class TestFileSizeValidation:
    """Test file size validation."""
    
    def test_normal_file_size(self):
        """Test normal file size (10MB)."""
        is_valid, msg = validate_file_size(10 * 1024 * 1024)
        
        assert is_valid is True
        assert msg is None
    
    def test_large_file_warning(self):
        """Test large file triggers warning (60MB)."""
        is_valid, msg = validate_file_size(60 * 1024 * 1024)
        
        assert is_valid is True
        assert msg is not None
        assert "large file" in msg.lower()
    
    def test_exceeds_max_size(self):
        """Test file exceeding max size is rejected (150MB)."""
        is_valid, msg = validate_file_size(150 * 1024 * 1024)
        
        assert is_valid is False
        assert msg is not None
        assert "exceeds limit" in msg.lower()
    
    def test_at_max_size_boundary(self):
        """Test file at exact max size limit."""
        is_valid, msg = validate_file_size(MAX_FILE_SIZE_BYTES)
        
        assert is_valid is True


@pytest.mark.asyncio
class TestSingleFileValidation:
    """Test single file validation with real file content."""
    
    async def test_valid_csv_file(self):
        """Test validation of valid CSV file."""
        csv_content = b"id,name,content\n1,Doc1,Sample text\n2,Doc2,More text"
        file_handle = io.BytesIO(csv_content)
        
        result = await validate_single_file("data.csv", file_handle, IngestMode.TEXT)
        
        assert result.filename == "data.csv"
        assert result.status == ValidationStatus.VALID
        assert len(result.errors) == 0
        assert result.file_size_bytes == len(csv_content)
    
    async def test_file_with_invalid_extension(self):
        """Test file with wrong extension for mode."""
        content = b"Some binary content"
        file_handle = io.BytesIO(content)
        
        result = await validate_single_file("document.pdf", file_handle, IngestMode.TEXT)
        
        assert result.status == ValidationStatus.INVALID
        assert len(result.errors) > 0
        assert any("extension" in err.lower() for err in result.errors)
    
    async def test_oversized_file(self):
        """Test file exceeding size limit."""
        # Create file larger than MAX_FILE_SIZE_BYTES
        large_content = b"x" * (MAX_FILE_SIZE_BYTES + 1000)
        file_handle = io.BytesIO(large_content)
        
        result = await validate_single_file("large.csv", file_handle, IngestMode.TEXT)
        
        assert result.status == ValidationStatus.INVALID
        assert any("exceeds limit" in err.lower() for err in result.errors)
    
    async def test_file_with_warning(self):
        """Test file that triggers warning but is valid."""
        # Create file larger than 50MB but under max
        large_content = b"x" * (60 * 1024 * 1024)
        file_handle = io.BytesIO(large_content)
        
        result = await validate_single_file("medium.csv", file_handle, IngestMode.TEXT)
        
        # Should be valid but have warning
        assert result.status == ValidationStatus.WARNING
        assert len(result.warnings) > 0
        assert any("large file" in warn.lower() for warn in result.warnings)


@pytest.mark.asyncio
class TestBatchFileValidation:
    """Test batch file validation."""
    
    async def test_valid_batch(self):
        """Test batch of all valid files."""
        files = [
            ("file1.csv", io.BytesIO(b"id,content\n1,text1")),
            ("file2.csv", io.BytesIO(b"id,content\n1,text2")),
            ("file3.csv", io.BytesIO(b"id,content\n1,text3")),
        ]
        
        summary = await validate_file_batch(files, IngestMode.TEXT)
        
        assert summary.total_files == 3
        assert summary.valid_files == 3
        assert summary.invalid_files == 0
        assert summary.can_proceed is True
        assert summary.overall_status == ValidationStatus.VALID
    
    async def test_mixed_batch(self):
        """Test batch with valid and invalid files."""
        files = [
            ("valid.csv", io.BytesIO(b"id,content\n1,text")),
            ("invalid.jpg", io.BytesIO(b"fake image data")),
            ("also_valid.txt", io.BytesIO(b"some text content")),
        ]
        
        summary = await validate_file_batch(files, IngestMode.TEXT)
        
        assert summary.total_files == 3
        assert summary.valid_files == 2
        assert summary.invalid_files == 1
        assert summary.can_proceed is True
        assert summary.overall_status == ValidationStatus.WARNING
    
    async def test_all_invalid_batch(self):
        """Test batch where all files are invalid."""
        files = [
            ("bad1.pdf", io.BytesIO(b"pdf content")),
            ("bad2.docx", io.BytesIO(b"doc content")),
        ]
        
        summary = await validate_file_batch(files, IngestMode.TEXT)
        
        assert summary.total_files == 2
        assert summary.valid_files == 0
        assert summary.invalid_files == 2
        assert summary.can_proceed is False
        assert summary.overall_status == ValidationStatus.INVALID
    
    async def test_batch_exceeds_file_limit(self):
        """Test batch exceeding maximum file count."""
        # Create more than MAX_BATCH_FILES
        files = [
            (f"file{i}.csv", io.BytesIO(b"data"))
            for i in range(MAX_BATCH_FILES + 1)
        ]
        
        summary = await validate_file_batch(files, IngestMode.TEXT)
        
        assert summary.can_proceed is False
        assert "exceeds maximum" in summary.summary_message.lower()
    
    async def test_empty_batch(self):
        """Test empty batch."""
        files = []
        
        summary = await validate_file_batch(files, IngestMode.TEXT)
        
        assert summary.total_files == 0
        assert summary.can_proceed is False

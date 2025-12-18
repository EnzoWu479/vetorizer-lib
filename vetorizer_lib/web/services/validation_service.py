"""File validation service for upload operations.

This module provides MIME type validation and batch file validation
to ensure uploaded files are compatible with the selected ingest mode.
"""

import magic
from pathlib import Path
from typing import BinaryIO

from vetorizer_lib.web.models.schemas import (
    FileValidationResult,
    BatchValidationSummary,
    ValidationStatus,
    IngestMode,
)


# File type configuration
ALLOWED_TYPES = {
    IngestMode.TEXT: {
        "extensions": {".csv", ".txt"},
        "mime_types": {"text/csv", "text/plain", "application/csv"},
    },
    IngestMode.IMAGE: {
        "extensions": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"},
        "mime_types": {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/bmp",
            "image/webp",
        },
    },
    IngestMode.HYBRID: {
        "extensions": {".csv"},
        "mime_types": {"text/csv", "text/plain", "application/csv"},
    },
}

# Quota limits
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100MB
MAX_BATCH_SIZE_BYTES = 500 * 1024 * 1024  # 500MB
MAX_BATCH_FILES = 50


def validate_file_extension(filename: str, mode: IngestMode) -> tuple[bool, str | None]:
    """Validate file extension against allowed types for mode.
    
    Args:
        filename: Name of file to validate.
        mode: Ingest mode to validate against.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    file_path = Path(filename)
    extension = file_path.suffix.lower()
    
    allowed = ALLOWED_TYPES[mode]["extensions"]
    
    if extension not in allowed:
        return False, f"File extension '{extension}' not allowed for {mode.value} mode. Allowed: {', '.join(allowed)}"
    
    return True, None


def validate_mime_type(file_content: bytes, mode: IngestMode) -> tuple[bool, str | None, str | None]:
    """Validate file MIME type using python-magic.
    
    Args:
        file_content: First chunk of file content for detection.
        mode: Ingest mode to validate against.
        
    Returns:
        Tuple of (is_valid, error_message, detected_mime_type).
    """
    try:
        # Detect MIME type from content
        mime = magic.Magic(mime=True)
        detected_mime = mime.from_buffer(file_content)
        
        allowed = ALLOWED_TYPES[mode]["mime_types"]
        
        if detected_mime not in allowed:
            return False, f"MIME type '{detected_mime}' not allowed for {mode.value} mode", detected_mime
        
        return True, None, detected_mime
        
    except Exception as e:
        return False, f"Failed to detect MIME type: {str(e)}", None


def validate_file_size(file_size: int) -> tuple[bool, str | None]:
    """Validate file size against quota limits.
    
    Args:
        file_size: Size of file in bytes.
        
    Returns:
        Tuple of (is_valid, error_or_warning_message).
    """
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds limit of {MAX_FILE_SIZE_BYTES / 1024 / 1024:.0f}MB"
    
    # Warning for large files (>50MB)
    if file_size > 50 * 1024 * 1024:
        return True, f"Large file ({file_size / 1024 / 1024:.1f}MB) may slow processing"
    
    return True, None


async def validate_single_file(
    filename: str,
    file_handle: BinaryIO,
    mode: IngestMode,
) -> FileValidationResult:
    """Validate a single file for compatibility with ingest mode.
    
    Args:
        filename: Name of the file.
        file_handle: File handle for reading content.
        mode: Ingest mode to validate against.
        
    Returns:
        FileValidationResult with validation status and any errors/warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []
    
    # Get file size
    file_handle.seek(0, 2)  # Seek to end
    file_size = file_handle.tell()
    file_handle.seek(0)  # Reset to start
    
    # Validate file size
    size_valid, size_msg = validate_file_size(file_size)
    if not size_valid:
        errors.append(size_msg)  # type: ignore
    elif size_msg:
        warnings.append(size_msg)
    
    # Validate file extension
    ext_valid, ext_msg = validate_file_extension(filename, mode)
    if not ext_valid:
        errors.append(ext_msg)  # type: ignore
    
    # Validate MIME type (read first 8KB for detection)
    mime_type = None
    try:
        content_sample = file_handle.read(8192)
        file_handle.seek(0)  # Reset
        
        mime_valid, mime_msg, detected_mime = validate_mime_type(content_sample, mode)
        mime_type = detected_mime
        
        if not mime_valid:
            errors.append(mime_msg)  # type: ignore
    except Exception as e:
        errors.append(f"Failed to read file: {str(e)}")
    
    # Determine overall status
    if errors:
        status = ValidationStatus.INVALID
    elif warnings:
        status = ValidationStatus.WARNING
    else:
        status = ValidationStatus.VALID
    
    return FileValidationResult(
        filename=filename,
        status=status,
        errors=errors,
        warnings=warnings,
        file_size_bytes=file_size,
        mime_type=mime_type,
    )


async def validate_file_batch(
    files: list[tuple[str, BinaryIO]],
    mode: IngestMode,
) -> BatchValidationSummary:
    """Validate a batch of files for upload.
    
    Performs parallel validation of all files and returns detailed summary.
    
    Args:
        files: List of (filename, file_handle) tuples to validate.
        mode: Ingest mode to validate against.
        
    Returns:
        BatchValidationSummary with overall status and per-file results.
    """
    # Check batch limits
    total_files = len(files)
    
    if total_files > MAX_BATCH_FILES:
        return BatchValidationSummary(
            overall_status=ValidationStatus.INVALID,
            total_files=total_files,
            valid_files=0,
            warning_files=0,
            invalid_files=total_files,
            files=[],
            can_proceed=False,
            summary_message=f"Batch exceeds maximum of {MAX_BATCH_FILES} files",
        )
    
    # Calculate total batch size
    total_size = 0
    for _, fh in files:
        fh.seek(0, 2)
        total_size += fh.tell()
        fh.seek(0)
    
    if total_size > MAX_BATCH_SIZE_BYTES:
        return BatchValidationSummary(
            overall_status=ValidationStatus.INVALID,
            total_files=total_files,
            valid_files=0,
            warning_files=0,
            invalid_files=total_files,
            files=[],
            can_proceed=False,
            summary_message=f"Batch size ({total_size / 1024 / 1024:.1f}MB) exceeds limit of {MAX_BATCH_SIZE_BYTES / 1024 / 1024:.0f}MB",
        )
    
    # Validate each file
    # Note: For MVP, sequential validation. Can parallelize with asyncio.gather for optimization.
    results: list[FileValidationResult] = []
    for filename, file_handle in files:
        result = await validate_single_file(filename, file_handle, mode)
        results.append(result)
    
    # Calculate summary statistics
    valid_count = sum(1 for r in results if r.status == ValidationStatus.VALID)
    warning_count = sum(1 for r in results if r.status == ValidationStatus.WARNING)
    invalid_count = sum(1 for r in results if r.status == ValidationStatus.INVALID)
    
    # Determine overall status
    if invalid_count == total_files:
        overall = ValidationStatus.INVALID
        summary_msg = f"✗ All {total_files} files failed validation"
    elif valid_count + warning_count == total_files:
        overall = ValidationStatus.VALID
        summary_msg = f"✓ All {total_files} files validated successfully"
    else:
        overall = ValidationStatus.WARNING
        summary_msg = f"⚠ {valid_count + warning_count}/{total_files} files valid, {invalid_count} failed"
    
    can_proceed = (valid_count + warning_count) > 0
    
    return BatchValidationSummary(
        overall_status=overall,
        total_files=total_files,
        valid_files=valid_count,
        warning_files=warning_count,
        invalid_files=invalid_count,
        files=results,
        can_proceed=can_proceed,
        summary_message=summary_msg,
    )

"""CSV ingestion utilities for vetorizer_lib.

This module provides functions for reading and processing CSV files
with chunked/batched processing for memory efficiency.
"""

from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pandas as pd

from vetorizer_lib.exceptions import ConfigurationError, IngestError
from vetorizer_lib.models.config import IngestConfig
from vetorizer_lib.models.document import ContentType, Document


def read_csv_batches(
    config: IngestConfig,
    content_type: ContentType = ContentType.TEXT,
) -> Generator[list[Document], None, None]:
    """Read a CSV file and yield batches of Document objects.

    This function uses pandas chunked reading to process large CSV files
    without loading them entirely into memory.

    Args:
        config: Ingestion configuration specifying file path, columns, etc.
        content_type: Type of content being ingested (text or image).

    Yields:
        Lists of Document objects, one batch at a time.

    Raises:
        IngestError: If the file cannot be read.
        ConfigurationError: If required columns are missing.

    Example:
        >>> config = IngestConfig(
        ...     file_path="data.csv",
        ...     content_column="description",
        ...     batch_size=100
        ... )
        >>> for batch in read_csv_batches(config):
        ...     print(f"Processing {len(batch)} documents")
    """
    file_path = Path(config.file_path)

    if not file_path.exists():
        raise IngestError(f"CSV file not found: {config.file_path}")

    try:
        # Read first chunk to validate columns
        sample = pd.read_csv(file_path, nrows=0)
        columns = set(sample.columns)
    except Exception as e:
        raise IngestError(f"Cannot read CSV file: {config.file_path}", cause=e) from e

    # Validate content column exists
    if config.content_column not in columns:
        raise ConfigurationError(
            f"Content column '{config.content_column}' not found in CSV. "
            f"Available columns: {', '.join(sorted(columns))}"
        )

    # Validate image column for image/hybrid modes
    if content_type in (ContentType.IMAGE, ContentType.HYBRID):
        if not config.image_column:
            raise ConfigurationError(
                f"image_column is required for {content_type.value} mode"
            )
        if config.image_column not in columns:
            raise ConfigurationError(
                f"Image column '{config.image_column}' not found in CSV. "
                f"Available columns: {', '.join(sorted(columns))}"
            )

    # Validate id column if specified
    if config.id_column and config.id_column not in columns:
        raise ConfigurationError(
            f"ID column '{config.id_column}' not found in CSV. "
            f"Available columns: {', '.join(sorted(columns))}"
        )

    # Validate metadata columns
    for col in config.metadata_columns:
        if col not in columns:
            raise ConfigurationError(
                f"Metadata column '{col}' not found in CSV. "
                f"Available columns: {', '.join(sorted(columns))}"
            )

    # Read CSV in chunks
    try:
        chunks = pd.read_csv(file_path, chunksize=config.batch_size)
    except Exception as e:
        raise IngestError(f"Cannot read CSV file: {config.file_path}", cause=e) from e

    for chunk in chunks:
        documents: list[Document] = []

        for _, row in chunk.iterrows():
            # Handle text content for TEXT and HYBRID modes
            if content_type in (ContentType.TEXT, ContentType.HYBRID):
                content = row[config.content_column]

                # Handle empty text content
                if pd.isna(content) or str(content).strip() == "":
                    if config.skip_empty:
                        continue
                    content = ""
                else:
                    content = str(content)
            else:
                # IMAGE mode: content is the image path
                content = row.get(config.image_column) if config.image_column else ""

            # Handle image path for IMAGE and HYBRID modes
            if content_type in (ContentType.IMAGE, ContentType.HYBRID):
                image_path_str = row.get(config.image_column, "")
                
                # Skip if image path is empty
                if pd.isna(image_path_str) or str(image_path_str).strip() == "":
                    if config.skip_empty:
                        continue
                
                # Resolve image path
                image_path = Path(str(image_path_str).strip())
                if config.base_path and not image_path.is_absolute():
                    image_path = Path(config.base_path) / image_path
                
                # Skip if image file doesn't exist
                if not image_path.exists():
                    if config.skip_empty:
                        continue
                
                # Skip if image can't be opened (corrupted)
                if config.skip_empty:
                    try:
                        from PIL import Image
                        Image.open(image_path).close()
                    except Exception:
                        continue
                
                # For IMAGE mode, content is the absolute path
                if content_type == ContentType.IMAGE:
                    content = str(image_path.absolute())

            # Get or generate ID
            if config.id_column:
                doc_id = str(row[config.id_column])
            else:
                doc_id = str(uuid4())

            # Build metadata
            metadata: dict[str, str | int | float | bool] = {}
            for col in config.metadata_columns:
                value = row[col]
                if not pd.isna(value):
                    metadata[col] = value
            
            # Add image_path to metadata for HYBRID mode
            if content_type == ContentType.HYBRID and config.image_column:
                image_path_value = row.get(config.image_column)
                if not pd.isna(image_path_value):
                    resolved_path = Path(str(image_path_value).strip())
                    if config.base_path and not resolved_path.is_absolute():
                        resolved_path = Path(config.base_path) / resolved_path
                    metadata["image_path"] = str(resolved_path.absolute())

            doc = Document(
                id=doc_id,
                content=content,
                content_type=content_type,
                metadata=metadata,
            )
            documents.append(doc)

        if documents:
            yield documents


def read_hybrid_csv_batches(
    *,
    file_path: str,
    text_column: str,
    image_column: str,
    id_column: str | None = None,
    metadata_columns: list[str] | None = None,
    batch_size: int = 100,
    skip_empty: bool = True,
) -> Generator[list[Document], None, None]:
    config = IngestConfig(
        file_path=file_path,
        content_column=text_column,
        id_column=id_column,
        metadata_columns=list(metadata_columns or []) + [image_column],
        batch_size=batch_size,
        skip_empty=skip_empty,
    )

    for batch in read_csv_batches(config, ContentType.TEXT):
        for doc in batch:
            if image_column in doc.metadata:
                continue
            doc.metadata[image_column] = ""
        yield batch

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
            content = row[config.content_column]

            # Handle empty content
            if pd.isna(content) or str(content).strip() == "":
                if config.skip_empty:
                    continue
                content = ""
            else:
                content = str(content)

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

            doc = Document(
                id=doc_id,
                content=content,
                content_type=content_type,
                metadata=metadata,
            )
            documents.append(doc)

        if documents:
            yield documents

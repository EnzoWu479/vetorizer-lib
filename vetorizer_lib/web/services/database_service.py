"""Database service for managing vector databases.

This module provides functions for creating, reading, updating, and deleting
vector database metadata using Qdrant-based MetadataStore.
"""

from vetorizer_lib.web.models.metadata_store import MetadataStore
from vetorizer_lib.web.models.schemas import DatabaseStatus, IngestMode, VectorDatabaseResponse


def create_database(
    store: MetadataStore,
    name: str,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    embedding_dimension: int = 384,
    ingest_mode: IngestMode = IngestMode.TEXT,
) -> VectorDatabaseResponse:
    """Create a new vector database entry.

    Args:
        store: MetadataStore instance.
        name: User-friendly database name.
        embedding_model: Name of the embedding model to use.
        embedding_dimension: Dimension of the embedding vectors.

    Returns:
        The created database response.

    Raises:
        ValueError: If a database with the same name already exists.

    Example:
        >>> store = MetadataStore(qdrant_path="./data/qdrant")
        >>> result = create_database(store, "my-products")
        >>> print(result.id)
    """
    return store.create_database(
        name,
        embedding_model,
        embedding_dimension,
        ingest_mode=ingest_mode,
    )


def get_database(store: MetadataStore, database_id: str) -> VectorDatabaseResponse | None:
    """Get a vector database by ID.

    Args:
        store: MetadataStore instance.
        database_id: The database UUID.

    Returns:
        The database response or None if not found.

    Example:
        >>> store = MetadataStore(qdrant_path="./data/qdrant")
        >>> result = get_database(store, "some-uuid")
    """
    return store.get_database(database_id)


def get_database_by_name(store: MetadataStore, name: str) -> VectorDatabaseResponse | None:
    """Get a vector database by name.

    Args:
        store: MetadataStore instance.
        name: The database name.

    Returns:
        The database response or None if not found.
    """
    return store._find_database_by_name(name)


def list_databases(store: MetadataStore) -> list[VectorDatabaseResponse]:
    """List all vector databases.

    Args:
        store: MetadataStore instance.

    Returns:
        List of all database responses.

    Example:
        >>> store = MetadataStore(qdrant_path="./data/qdrant")
        >>> databases = list_databases(store)
        >>> for db in databases:
        ...     print(db.name)
    """
    return store.list_databases()


def update_database_status(
    store: MetadataStore,
    database_id: str,
    status: DatabaseStatus,
    document_count: int | None = None,
) -> None:
    """Update the status of a vector database.

    Args:
        store: MetadataStore instance.
        database_id: The database UUID.
        status: New status.
        document_count: Optional new document count.
    """
    store.update_database(database_id, status=status, document_count=document_count)


def update_database_name(
    store: MetadataStore,
    database_id: str,
    new_name: str,
) -> VectorDatabaseResponse | None:
    """Update the name of a vector database.

    Args:
        store: MetadataStore instance.
        database_id: The database UUID.
        new_name: New database name.

    Returns:
        Updated database response or None if not found.

    Raises:
        ValueError: If new name already exists.
    """
    return store.update_database(database_id, name=new_name)


def delete_database(store: MetadataStore, database_id: str) -> bool:
    """Delete a vector database.

    Args:
        store: MetadataStore instance.
        database_id: The database UUID.

    Returns:
        True if deleted, False if not found.
    """
    return store.delete_database(database_id)


async def create_database_with_files(
    store: MetadataStore,
    name: str,
    ingest_mode: IngestMode,
    files: list[tuple[str, any]],
    text_column: str | None = None,
    image_column: str | None = None,
    id_column: str | None = None,
    metadata_columns: list[str] | None = None,
    text_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    image_embedding_model: str = "openai/clip-vit-base-patch16",
) -> tuple[VectorDatabaseResponse, dict[str, any]]:
    """Create database and ingest files in a transactional operation.
    
    This function:
    1. Creates the database metadata
    2. Validates and ingests files
    3. Updates database status to READY on success
    4. Rolls back (deletes database) on failure
    
    Args:
        store: MetadataStore instance.
        name: Database name.
        ingest_mode: Mode for ingestion (text/image/hybrid).
        files: List of (filename, file_handle) tuples.
        text_column: Column name for text content.
        image_column: Column name for image paths/URLs.
        id_column: Optional column name for document IDs.
        metadata_columns: Optional list of metadata column names.
        text_embedding_model: Model for text embeddings.
        image_embedding_model: Model for image embeddings.
        
    Returns:
        Tuple of (VectorDatabaseResponse, ingestion_stats dict).
        
    Raises:
        ValueError: If database name already exists or validation fails.
    """
    import time
    from vetorizer_lib.embedders.manager import embedder_manager
    
    start_time = time.time()
    
    # Determine dimensions based on mode
    if ingest_mode == IngestMode.TEXT:
        text_dim = embedder_manager.get_text_dimension(text_embedding_model)
        total_dimension = text_dim
        text_embedding_dimension = text_dim
        image_embedding_dimension = None
    elif ingest_mode == IngestMode.IMAGE:
        image_dim = embedder_manager.get_image_dimension(image_embedding_model)
        total_dimension = image_dim
        text_embedding_dimension = None
        image_embedding_dimension = image_dim
    else:  # HYBRID
        text_dim = embedder_manager.get_text_dimension(text_embedding_model)
        image_dim = embedder_manager.get_image_dimension(image_embedding_model)
        total_dimension = text_dim + image_dim
        text_embedding_dimension = text_dim
        image_embedding_dimension = image_dim
    
    # Step 1: Create database metadata
    try:
        database = store.create_database(
            name=name,
            embedding_model=text_embedding_model,  # For compatibility
            embedding_dimension=total_dimension,
            ingest_mode=ingest_mode,
            text_embedding_model=text_embedding_model if ingest_mode in [IngestMode.TEXT, IngestMode.HYBRID] else None,
            image_embedding_model=image_embedding_model if ingest_mode in [IngestMode.IMAGE, IngestMode.HYBRID] else None,
            text_embedding_dimension=text_embedding_dimension,
            image_embedding_dimension=image_embedding_dimension,
        )
    except ValueError as e:
        raise ValueError(f"Failed to create database: {str(e)}")
    
    # Step 2: Ingest files (simplified for MVP - full implementation in later tasks)
    documents_processed = 0
    documents_ignored = 0
    documents_failed = 0
    errors: list[str] = []
    
    try:
        # TODO: Implement actual CSV ingestion in Phase 4 (User Story 1)
        # For now, just validate files are accessible
        for filename, file_handle in files:
            try:
                # Check if file is readable
                file_handle.seek(0)
                content = file_handle.read(100)  # Read first 100 bytes
                file_handle.seek(0)
                
                if len(content) > 0:
                    documents_processed += 1
                else:
                    documents_ignored += 1
                    errors.append(f"{filename}: Empty file")
            except Exception as e:
                documents_failed += 1
                errors.append(f"{filename}: {str(e)}")
        
        # Step 3: Update database status to READY
        store.update_database(
            database.id,
            status=DatabaseStatus.READY,
            document_count=documents_processed,
        )
        
        processing_time = time.time() - start_time
        
        ingestion_stats = {
            "database_id": database.id,
            "database_name": database.name,
            "total_files": len(files),
            "documents_processed": documents_processed,
            "documents_ignored": documents_ignored,
            "documents_failed": documents_failed,
            "processing_time_seconds": processing_time,
            "errors": errors,
        }
        
        return database, ingestion_stats
        
    except Exception as e:
        # Rollback: Delete database on failure
        try:
            store.delete_database(database.id)
        except Exception:
            pass  # Best effort cleanup
        
        raise ValueError(f"Ingestion failed: {str(e)}")

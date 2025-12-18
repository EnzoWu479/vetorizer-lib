"""Database service for managing vector databases.

This module provides functions for creating, reading, updating, and deleting
vector database metadata using Qdrant-based MetadataStore.
"""

from vetorizer_lib.web.models.metadata_store import MetadataStore
from vetorizer_lib.web.models.schemas import DatabaseStatus, VectorDatabaseResponse


def create_database(
    store: MetadataStore,
    name: str,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    embedding_dimension: int = 384,
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
    return store.create_database(name, embedding_model, embedding_dimension)


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

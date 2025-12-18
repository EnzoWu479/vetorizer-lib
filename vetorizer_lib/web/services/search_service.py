"""Search service for vector database queries.

This module provides functions for searching vector databases
using text and image queries via Qdrant-based MetadataStore.
"""

import time
import uuid

from vetorizer_lib.web.models.metadata_store import MetadataStore
from vetorizer_lib.web.models.schemas import SearchResultItem, SearchResponse
from vetorizer_lib.web.services.database_service import get_database


def search_text(
    store: MetadataStore,
    database_ids: list[str],
    query: str,
    limit: int = 10,
    min_score: float | None = None,
    qdrant_url: str | None = None,
    qdrant_path: str | None = "./data/qdrant",
) -> SearchResponse:
    """Search vector databases using a text query.

    Args:
        store: MetadataStore instance for metadata lookup.
        database_ids: List of database UUIDs to search.
        query: Text query to search for.
        limit: Maximum results per database.
        min_score: Minimum similarity score (0-1).
        qdrant_url: URL for remote Qdrant server.
        qdrant_path: Path to Qdrant storage (local mode).

    Returns:
        SearchResponse with results grouped by database.

    Raises:
        ValueError: If any database ID is invalid.

    Example:
        >>> store = MetadataStore(qdrant_path="./data/qdrant")
        >>> response = search_text(store, ["db-uuid"], "running shoes")
        >>> for db_id, results in response.results.items():
        ...     print(f"{db_id}: {len(results)} results")
    """
    from vetorizer_lib.client import VetorizerClient

    start_time = time.time()
    query_id = str(uuid.uuid4())
    all_results: dict[str, list[SearchResultItem]] = {}
    total_results = 0

    for database_id in database_ids:
        # Get database metadata
        database = get_database(store, database_id)
        if not database:
            raise ValueError(f"Database '{database_id}' not found")

        # Initialize client for this database's collection
        client = VetorizerClient(
            qdrant_url=qdrant_url,
            qdrant_path=qdrant_path,
            collection_name=database.collection_name,
        )

        # Perform search
        try:
            search_results = client.search(query=query, limit=limit)

            # Convert to response format
            db_results: list[SearchResultItem] = []
            for result in search_results:
                score = result.score if hasattr(result, 'score') else 0.0

                # Apply minimum score filter
                if min_score is not None and score < min_score:
                    continue

                db_results.append(SearchResultItem(
                    id=str(result.id) if hasattr(result, 'id') else str(uuid.uuid4()),
                    content=result.content if hasattr(result, 'content') else str(result.payload.get('content', '')),
                    score=score,
                    metadata=result.payload if hasattr(result, 'payload') else None,
                    database_id=database_id,
                    database_name=database.name,
                ))

            all_results[database_id] = db_results
            total_results += len(db_results)

        except Exception as e:
            # If search fails for a database, return empty results for it
            all_results[database_id] = []

    query_time_ms = int((time.time() - start_time) * 1000)

    return SearchResponse(
        query_id=query_id,
        results=all_results,
        total_results=total_results,
        query_time_ms=query_time_ms,
    )


def search_image(
    store: MetadataStore,
    database_ids: list[str],
    image_path: str,
    limit: int = 10,
    min_score: float | None = None,
    qdrant_url: str | None = None,
    qdrant_path: str | None = "./data/qdrant",
) -> SearchResponse:
    """Search vector databases using an image query.

    Args:
        store: MetadataStore instance for metadata lookup.
        database_ids: List of database UUIDs to search.
        image_path: Path to the query image.
        limit: Maximum results per database.
        min_score: Minimum similarity score (0-1).
        qdrant_url: URL for remote Qdrant server.
        qdrant_path: Path to Qdrant storage (local mode).

    Returns:
        SearchResponse with results grouped by database.

    Raises:
        ValueError: If any database ID is invalid.
    """
    from vetorizer_lib.client import VetorizerClient

    start_time = time.time()
    query_id = str(uuid.uuid4())
    all_results: dict[str, list[SearchResultItem]] = {}
    total_results = 0

    for database_id in database_ids:
        # Get database metadata
        database = get_database(store, database_id)
        if not database:
            raise ValueError(f"Database '{database_id}' not found")

        # Initialize client for this database's collection
        client = VetorizerClient(
            qdrant_url=qdrant_url,
            qdrant_path=qdrant_path,
            collection_name=database.collection_name,
        )

        # Perform image search
        try:
            search_results = client.search_by_image(image_path=image_path, limit=limit)

            # Convert to response format
            db_results: list[SearchResultItem] = []
            for result in search_results:
                score = result.score if hasattr(result, 'score') else 0.0

                # Apply minimum score filter
                if min_score is not None and score < min_score:
                    continue

                db_results.append(SearchResultItem(
                    id=str(result.id) if hasattr(result, 'id') else str(uuid.uuid4()),
                    content=result.content if hasattr(result, 'content') else str(result.payload.get('content', '')),
                    score=score,
                    metadata=result.payload if hasattr(result, 'payload') else None,
                    database_id=database_id,
                    database_name=database.name,
                ))

            all_results[database_id] = db_results
            total_results += len(db_results)

        except Exception as e:
            # If search fails for a database, return empty results for it
            all_results[database_id] = []

    query_time_ms = int((time.time() - start_time) * 1000)

    return SearchResponse(
        query_id=query_id,
        results=all_results,
        total_results=total_results,
        query_time_ms=query_time_ms,
    )

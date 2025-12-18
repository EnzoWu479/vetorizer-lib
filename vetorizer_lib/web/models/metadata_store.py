"""Qdrant-based metadata storage for web UI.

This module provides the MetadataStore class for storing vector database
metadata and upload job tracking in a special Qdrant collection.
Replaces the previous SQLite-based storage.
"""

import uuid
from datetime import datetime
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from vetorizer_lib.web.models.schemas import (
    DatabaseStatus,
    IngestMode,
    UploadStatus,
    VectorDatabaseResponse,
    UploadJobResponse,
)


# Collection name for metadata storage
METADATA_COLLECTION = "_vetorizer_metadata"
# Dummy vector size (metadata doesn't need real vectors)
METADATA_VECTOR_SIZE = 4


def _sanitize_collection_name(name: str) -> str:
    """Convert a user-friendly name to a valid Qdrant collection name.

    Args:
        name: User-provided database name.

    Returns:
        Sanitized collection name safe for Qdrant.
    """
    sanitized = name.lower().replace(" ", "_").replace("-", "_")
    sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
    if not sanitized:
        sanitized = "collection"
    return f"vdb_{sanitized}_{uuid.uuid4().hex[:8]}"


class MetadataStore:
    """Qdrant-based metadata storage for vector databases and upload jobs.

    Uses a special collection `_vetorizer_metadata` to store metadata as
    points with payloads. Each point has a dummy vector (metadata doesn't
    need similarity search) and a payload containing the actual metadata.

    Supports both file-based storage (qdrant_path) and remote Qdrant server (qdrant_url).

    Attributes:
        qdrant_path: Path to Qdrant file-based storage (if using local mode).
        qdrant_url: URL for remote Qdrant server (if using remote mode).

    Example:
        >>> # Local file-based storage
        >>> store = MetadataStore(qdrant_path="./data/qdrant")
        >>> # Remote Qdrant server
        >>> store = MetadataStore(qdrant_url="http://localhost:6333")
        >>> db = store.create_database("my-products")
        >>> print(db.id)
    """

    def __init__(
        self,
        qdrant_path: str | None = None,
        qdrant_url: str | None = None,
        qdrant_api_key: str | None = None,
    ) -> None:
        """Initialize the metadata store.

        Args:
            qdrant_path: Path to Qdrant file-based storage directory (local mode).
            qdrant_url: URL for remote Qdrant server (remote mode).
            qdrant_api_key: API key for Qdrant Cloud (optional, for remote mode).

        Raises:
            ValueError: If neither qdrant_path nor qdrant_url is provided.
        """
        self._qdrant_path = qdrant_path
        self._qdrant_url = qdrant_url
        self._qdrant_api_key = qdrant_api_key

        if qdrant_url:
            # Remote Qdrant server
            self._client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
            )
        elif qdrant_path:
            # Local file-based storage
            self._client = QdrantClient(path=qdrant_path)
        else:
            raise ValueError("Either qdrant_path or qdrant_url must be provided")

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Ensure the metadata collection exists."""
        if not self._client.collection_exists(METADATA_COLLECTION):
            self._client.create_collection(
                collection_name=METADATA_COLLECTION,
                vectors_config=VectorParams(
                    size=METADATA_VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

    def _dummy_vector(self) -> list[float]:
        """Return a dummy vector for metadata points."""
        return [0.0] * METADATA_VECTOR_SIZE

    # -------------------------------------------------------------------------
    # Database CRUD
    # -------------------------------------------------------------------------

    def create_database(
        self,
        name: str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_dimension: int = 384,
        ingest_mode: IngestMode = IngestMode.TEXT,
        text_embedding_model: str | None = None,
        image_embedding_model: str | None = None,
        text_embedding_dimension: int | None = None,
        image_embedding_dimension: int | None = None,
    ) -> VectorDatabaseResponse:
        """Create a new vector database entry.

        Args:
            name: User-friendly database name.
            embedding_model: Name of the embedding model to use.
            embedding_dimension: Dimension of the embedding vectors.

        Returns:
            The created database response.

        Raises:
            ValueError: If a database with the same name already exists.
        """
        # Check if name already exists
        existing = self._find_database_by_name(name)
        if existing:
            raise ValueError(f"Database with name '{name}' already exists")

        database_id = str(uuid.uuid4())
        collection_name = _sanitize_collection_name(name)
        now = datetime.utcnow().isoformat()

        payload = {
            "type": "database",
            "id": database_id,
            "name": name,
            "collection_name": collection_name,
            "document_count": 0,
            "embedding_model": embedding_model,
            "embedding_dimension": embedding_dimension,
            "ingest_mode": ingest_mode.value,
            "text_embedding_model": text_embedding_model,
            "image_embedding_model": image_embedding_model,
            "text_embedding_dimension": text_embedding_dimension,
            "image_embedding_dimension": image_embedding_dimension,
            "status": DatabaseStatus.CREATING.value,
            "created_at": now,
            "updated_at": now,
        }

        self._client.upsert(
            collection_name=METADATA_COLLECTION,
            points=[
                PointStruct(
                    id=database_id,
                    vector=self._dummy_vector(),
                    payload=payload,
                )
            ],
        )

        return VectorDatabaseResponse(
            id=database_id,
            name=name,
            collection_name=collection_name,
            document_count=0,
            embedding_model=embedding_model,
            embedding_dimension=embedding_dimension,
            ingest_mode=ingest_mode,
            text_embedding_model=text_embedding_model,
            image_embedding_model=image_embedding_model,
            text_embedding_dimension=text_embedding_dimension,
            image_embedding_dimension=image_embedding_dimension,
            status=DatabaseStatus.CREATING,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )

    def get_database(self, database_id: str) -> VectorDatabaseResponse | None:
        """Get a vector database by ID.

        Args:
            database_id: The database UUID.

        Returns:
            The database response or None if not found.
        """
        try:
            records = self._client.retrieve(
                collection_name=METADATA_COLLECTION,
                ids=[database_id],
                with_payload=True,
            )
            if not records:
                return None

            payload = records[0].payload
            if not payload or payload.get("type") != "database":
                return None

            return self._payload_to_database(payload)
        except Exception:
            return None

    def _find_database_by_name(self, name: str) -> VectorDatabaseResponse | None:
        """Find a database by name.

        Args:
            name: Database name to search for.

        Returns:
            The database response or None if not found.
        """
        records, _ = self._client.scroll(
            collection_name=METADATA_COLLECTION,
            scroll_filter=Filter(
                must=[
                    FieldCondition(key="type", match=MatchValue(value="database")),
                    FieldCondition(key="name", match=MatchValue(value=name)),
                ]
            ),
            limit=1,
            with_payload=True,
        )
        if not records:
            return None

        return self._payload_to_database(records[0].payload)

    def list_databases(self) -> list[VectorDatabaseResponse]:
        """List all vector databases.

        Returns:
            List of database responses.
        """
        all_databases: list[VectorDatabaseResponse] = []
        offset = None

        while True:
            records, next_offset = self._client.scroll(
                collection_name=METADATA_COLLECTION,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="type", match=MatchValue(value="database")),
                    ]
                ),
                limit=100,
                offset=offset,
                with_payload=True,
            )

            for record in records:
                if record.payload:
                    all_databases.append(self._payload_to_database(record.payload))

            if next_offset is None:
                break
            offset = next_offset

        return all_databases

    def update_database(
        self,
        database_id: str,
        name: str | None = None,
        status: DatabaseStatus | None = None,
        document_count: int | None = None,
        ingest_mode: IngestMode | None = None,
        text_embedding_model: str | None = None,
        image_embedding_model: str | None = None,
        text_embedding_dimension: int | None = None,
        image_embedding_dimension: int | None = None,
    ) -> VectorDatabaseResponse | None:
        """Update a vector database.

        Args:
            database_id: The database UUID.
            name: New name (optional).
            status: New status (optional).
            document_count: New document count (optional).

        Returns:
            The updated database response or None if not found.

        Raises:
            ValueError: If new name conflicts with existing database.
        """
        db = self.get_database(database_id)
        if not db:
            return None

        # Check name uniqueness if changing
        if name and name != db.name:
            existing = self._find_database_by_name(name)
            if existing:
                raise ValueError(f"Database with name '{name}' already exists")

        now = datetime.utcnow().isoformat()

        payload = {
            "type": "database",
            "id": database_id,
            "name": name if name else db.name,
            "collection_name": db.collection_name,
            "document_count": document_count if document_count is not None else db.document_count,
            "embedding_model": db.embedding_model,
            "embedding_dimension": db.embedding_dimension,
            "ingest_mode": (ingest_mode.value if ingest_mode else db.ingest_mode.value),
            "text_embedding_model": (
                text_embedding_model if text_embedding_model is not None else db.text_embedding_model
            ),
            "image_embedding_model": (
                image_embedding_model if image_embedding_model is not None else db.image_embedding_model
            ),
            "text_embedding_dimension": (
                text_embedding_dimension
                if text_embedding_dimension is not None
                else db.text_embedding_dimension
            ),
            "image_embedding_dimension": (
                image_embedding_dimension
                if image_embedding_dimension is not None
                else db.image_embedding_dimension
            ),
            "status": status.value if status else db.status.value,
            "created_at": db.created_at.isoformat(),
            "updated_at": now,
        }

        self._client.upsert(
            collection_name=METADATA_COLLECTION,
            points=[
                PointStruct(
                    id=database_id,
                    vector=self._dummy_vector(),
                    payload=payload,
                )
            ],
        )

        return self._payload_to_database(payload)

    def delete_database(self, database_id: str) -> bool:
        """Delete a vector database and its associated upload jobs.

        Args:
            database_id: The database UUID.

        Returns:
            True if deleted, False if not found.
        """
        db = self.get_database(database_id)
        if not db:
            return False

        # Delete the database metadata point
        self._client.delete(
            collection_name=METADATA_COLLECTION,
            points_selector=[database_id],
        )

        # Delete associated upload jobs
        jobs = self.list_upload_jobs(database_id)
        if jobs:
            job_ids = [job.id for job in jobs]
            self._client.delete(
                collection_name=METADATA_COLLECTION,
                points_selector=job_ids,
            )

        # Delete the actual vector collection
        if self._client.collection_exists(db.collection_name):
            self._client.delete_collection(db.collection_name)

        return True

    def _payload_to_database(self, payload: dict[str, Any]) -> VectorDatabaseResponse:
        """Convert a payload dict to VectorDatabaseResponse."""
        return VectorDatabaseResponse(
            id=payload["id"],
            name=payload["name"],
            collection_name=payload["collection_name"],
            document_count=payload.get("document_count", 0),
            embedding_model=payload.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
            embedding_dimension=payload.get("embedding_dimension", 384),
            ingest_mode=IngestMode(payload.get("ingest_mode", IngestMode.TEXT.value)),
            text_embedding_model=payload.get("text_embedding_model"),
            image_embedding_model=payload.get("image_embedding_model"),
            text_embedding_dimension=payload.get("text_embedding_dimension"),
            image_embedding_dimension=payload.get("image_embedding_dimension"),
            status=DatabaseStatus(payload.get("status", "CREATING")),
            created_at=datetime.fromisoformat(payload["created_at"]),
            updated_at=datetime.fromisoformat(payload["updated_at"]),
        )

    # -------------------------------------------------------------------------
    # Upload Job CRUD
    # -------------------------------------------------------------------------

    def create_upload_job(
        self,
        database_id: str,
        filename: str,
        file_size_bytes: int,
        content_column: str,
        ingest_mode: IngestMode = IngestMode.TEXT,
        text_column: str | None = None,
        image_column: str | None = None,
        id_column: str | None = None,
        metadata_columns: list[str] | None = None,
    ) -> UploadJobResponse:
        """Create a new upload job.

        Args:
            database_id: Target database UUID.
            filename: Original filename.
            file_size_bytes: File size in bytes.
            content_column: CSV column containing text to embed.
            id_column: Optional CSV column for document IDs.
            metadata_columns: Optional list of metadata columns.

        Returns:
            The created upload job response.
        """
        job_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        payload = {
            "type": "upload_job",
            "id": job_id,
            "database_id": database_id,
            "filename": filename,
            "file_size_bytes": file_size_bytes,
            "content_column": content_column,
            "ingest_mode": ingest_mode.value,
            "text_column": text_column,
            "image_column": image_column,
            "id_column": id_column,
            "metadata_columns": metadata_columns or [],
            "status": UploadStatus.PENDING.value,
            "progress_percent": 0,
            "documents_processed": 0,
            "documents_failed": 0,
            "error_message": None,
            "started_at": None,
            "completed_at": None,
            "created_at": now,
        }

        self._client.upsert(
            collection_name=METADATA_COLLECTION,
            points=[
                PointStruct(
                    id=job_id,
                    vector=self._dummy_vector(),
                    payload=payload,
                )
            ],
        )

        return UploadJobResponse(
            id=job_id,
            database_id=database_id,
            filename=filename,
            file_size_bytes=file_size_bytes,
            content_column=content_column,
            ingest_mode=ingest_mode,
            text_column=text_column,
            image_column=image_column,
            id_column=id_column,
            metadata_columns=metadata_columns or [],
            status=UploadStatus.PENDING,
            progress_percent=0,
            documents_processed=0,
            documents_failed=0,
            error_message=None,
            started_at=None,
            completed_at=None,
            created_at=datetime.fromisoformat(now),
        )

    def get_upload_job(self, job_id: str) -> UploadJobResponse | None:
        """Get an upload job by ID.

        Args:
            job_id: The job UUID.

        Returns:
            The upload job response or None if not found.
        """
        try:
            records = self._client.retrieve(
                collection_name=METADATA_COLLECTION,
                ids=[job_id],
                with_payload=True,
            )
            if not records:
                return None

            payload = records[0].payload
            if not payload or payload.get("type") != "upload_job":
                return None

            return self._payload_to_upload_job(payload)
        except Exception:
            return None

    def list_upload_jobs(self, database_id: str) -> list[UploadJobResponse]:
        """List upload jobs for a database.

        Args:
            database_id: The database UUID.

        Returns:
            List of upload job responses.
        """
        records, _ = self._client.scroll(
            collection_name=METADATA_COLLECTION,
            scroll_filter=Filter(
                must=[
                    FieldCondition(key="type", match=MatchValue(value="upload_job")),
                    FieldCondition(key="database_id", match=MatchValue(value=database_id)),
                ]
            ),
            limit=100,
            with_payload=True,
        )

        return [self._payload_to_upload_job(r.payload) for r in records if r.payload]

    def update_upload_job(
        self,
        job_id: str,
        status: UploadStatus | None = None,
        progress_percent: int | None = None,
        documents_processed: int | None = None,
        documents_failed: int | None = None,
        error_message: str | None = None,
    ) -> UploadJobResponse | None:
        """Update an upload job.

        Args:
            job_id: The job UUID.
            status: New status (optional).
            progress_percent: New progress percentage (optional).
            documents_processed: New processed count (optional).
            documents_failed: New failed count (optional).
            error_message: Error message (optional).

        Returns:
            The updated upload job response or None if not found.
        """
        job = self.get_upload_job(job_id)
        if not job:
            return None

        now = datetime.utcnow()

        # Determine timestamps
        started_at = job.started_at
        completed_at = job.completed_at

        if status == UploadStatus.PROCESSING and not started_at:
            started_at = now
        if status in (UploadStatus.COMPLETED, UploadStatus.FAILED):
            completed_at = now

        payload = {
            "type": "upload_job",
            "id": job_id,
            "database_id": job.database_id,
            "filename": job.filename,
            "file_size_bytes": job.file_size_bytes,
            "content_column": job.content_column,
            "ingest_mode": job.ingest_mode.value,
            "text_column": job.text_column,
            "image_column": job.image_column,
            "id_column": job.id_column,
            "metadata_columns": job.metadata_columns,
            "status": status.value if status else job.status.value,
            "progress_percent": progress_percent if progress_percent is not None else job.progress_percent,
            "documents_processed": documents_processed if documents_processed is not None else job.documents_processed,
            "documents_failed": documents_failed if documents_failed is not None else job.documents_failed,
            "error_message": error_message if error_message is not None else job.error_message,
            "started_at": started_at.isoformat() if started_at else None,
            "completed_at": completed_at.isoformat() if completed_at else None,
            "created_at": job.created_at.isoformat(),
        }

        self._client.upsert(
            collection_name=METADATA_COLLECTION,
            points=[
                PointStruct(
                    id=job_id,
                    vector=self._dummy_vector(),
                    payload=payload,
                )
            ],
        )

        return self._payload_to_upload_job(payload)

    def _payload_to_upload_job(self, payload: dict[str, Any]) -> UploadJobResponse:
        """Convert a payload dict to UploadJobResponse."""
        return UploadJobResponse(
            id=payload["id"],
            database_id=payload["database_id"],
            filename=payload["filename"],
            file_size_bytes=payload["file_size_bytes"],
            content_column=payload["content_column"],
            ingest_mode=IngestMode(payload.get("ingest_mode", IngestMode.TEXT.value)),
            text_column=payload.get("text_column"),
            image_column=payload.get("image_column"),
            id_column=payload.get("id_column"),
            metadata_columns=payload.get("metadata_columns", []),
            status=UploadStatus(payload.get("status", "PENDING")),
            progress_percent=payload.get("progress_percent", 0),
            documents_processed=payload.get("documents_processed", 0),
            documents_failed=payload.get("documents_failed", 0),
            error_message=payload.get("error_message"),
            started_at=datetime.fromisoformat(payload["started_at"]) if payload.get("started_at") else None,
            completed_at=datetime.fromisoformat(payload["completed_at"]) if payload.get("completed_at") else None,
            created_at=datetime.fromisoformat(payload["created_at"]),
        )


# Global metadata store instance
_metadata_store: MetadataStore | None = None


def get_metadata_store(qdrant_path: str) -> MetadataStore:
    """Get or create the global metadata store instance.

    Args:
        qdrant_path: Path to Qdrant file-based storage.

    Returns:
        MetadataStore instance.
    """
    global _metadata_store
    if _metadata_store is None:
        _metadata_store = MetadataStore(qdrant_path)
    return _metadata_store


def reset_metadata_store() -> None:
    """Reset the global metadata store instance (for testing)."""
    global _metadata_store
    _metadata_store = None

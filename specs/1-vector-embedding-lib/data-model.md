# Data Model: Vector Embedding Library

**Feature**: 1-vector-embedding-lib  
**Date**: 2025-12-17

## Entities

### Document

Represents a single item to be embedded and stored in the vector database.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | str | Unique identifier | Required, non-empty |
| content | str | Text content or image path | Required |
| embedding | list[float] | Vector representation | Generated, dimension matches model |
| metadata | dict[str, Any] | Additional key-value data | Optional, JSON-serializable |
| content_type | ContentType | "text" or "image" | Required |

**Validation Rules**:
- `id` must be unique within a collection
- `content` must be non-empty string
- `embedding` dimension must match the configured model's output dimension
- `metadata` values must be JSON-serializable (str, int, float, bool, list, dict)

---

### SearchResult

Represents a single result from a vector similarity search.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | str | Document ID | From stored document |
| score | float | Similarity score | 0.0 to 1.0 (cosine) |
| content | str | Original content | From stored document |
| metadata | dict[str, Any] | Document metadata | From stored document |

---

### EmbeddingModel

Configuration for the embedding model.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| name | str | HuggingFace model identifier | Valid model path |
| dimension | int | Output embedding dimension | Positive integer |
| modality | Modality | "text", "image", or "multimodal" | Enum value |

**Default Values**:
- Text: `sentence-transformers/all-MiniLM-L6-v2` (384 dims)
- Image: `openai/clip-vit-base-patch32` (512 dims)

---

### VectorStoreConfig

Configuration for connecting to the vector database.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| url | str \| None | Qdrant server URL | Valid URL or None for local |
| api_key | str \| None | API key for cloud Qdrant | Optional |
| collection_name | str | Name of the collection | Non-empty, alphanumeric + underscore |
| distance_metric | DistanceMetric | Similarity metric | "cosine", "euclidean", "dot" |
| path | str \| None | Local storage path | Optional, for file-based Qdrant |

**Default Values**:
- `distance_metric`: "cosine"
- `collection_name`: "default"

---

### IngestConfig

Configuration for CSV ingestion.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| file_path | str | Path to CSV file | Must exist, readable |
| content_column | str | Column containing content | Must exist in CSV |
| id_column | str \| None | Column for document IDs | Optional, auto-generate if None |
| metadata_columns | list[str] | Columns to include as metadata | Optional |
| batch_size | int | Documents per batch | Positive integer, default 100 |
| skip_empty | bool | Skip rows with empty content | Default True |

---

## Enums

### ContentType

```python
class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
```

### Modality

```python
class Modality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    MULTIMODAL = "multimodal"
```

### DistanceMetric

```python
class DistanceMetric(str, Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT = "dot"
```

---

## Relationships

```
┌─────────────────┐
│ VetorizerClient │
└────────┬────────┘
         │ uses
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌─────────────┐
│Embedder│  │ VectorStore │
└────────┘  └─────────────┘
    │              │
    │ configured   │ configured
    │ by           │ by
    ▼              ▼
┌──────────────┐  ┌──────────────────┐
│EmbeddingModel│  │VectorStoreConfig │
└──────────────┘  └──────────────────┘

┌────────────┐  ingested   ┌──────────┐
│IngestConfig│────────────▶│ Document │
└────────────┘             └──────────┘
                                │
                                │ stored in
                                ▼
                          ┌─────────────┐
                          │ VectorStore │
                          └─────────────┘
                                │
                                │ returns
                                ▼
                          ┌──────────────┐
                          │ SearchResult │
                          └──────────────┘
```

---

## State Transitions

### Document Lifecycle

```
[CSV Row] ──parse──▶ [Document(no embedding)] ──embed──▶ [Document(with embedding)] ──store──▶ [Stored in Qdrant]
```

### Ingestion States

```
[Pending] ──start──▶ [Processing] ──complete──▶ [Done]
                          │
                          │ error
                          ▼
                      [Failed]
```

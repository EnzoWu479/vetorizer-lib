# Data Model: Web GUI for Vector Database Management

**Feature**: 002-web-gui  
**Date**: 2024-12-17  
**Status**: Complete

## Overview

This document defines the data entities, their attributes, relationships, and validation rules for the Web GUI feature.

---

## Entities

### 1. VectorDatabase

Represents a named collection of embedded documents stored in Qdrant.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | string (UUID) | Primary key, auto-generated | Unique identifier |
| name | string | Unique, 1-100 chars, alphanumeric + spaces/hyphens | User-friendly display name |
| collection_name | string | Derived from name, lowercase, no spaces | Qdrant collection identifier |
| document_count | integer | >= 0 | Number of documents in the database |
| embedding_model | string | Non-empty | Model used for embeddings (e.g., "all-MiniLM-L6-v2") |
| embedding_dimension | integer | > 0 | Vector dimension (e.g., 384, 512, 768) |
| created_at | datetime | Auto-set on creation | Creation timestamp |
| updated_at | datetime | Auto-updated on modification | Last modification timestamp |

**Validation Rules**:
- `name` must be unique across all databases
- `name` must match pattern: `^[a-zA-Z0-9][a-zA-Z0-9 -]{0,98}[a-zA-Z0-9]$`
- `collection_name` is derived: `name.lower().replace(' ', '-').replace('--', '-')`

**State Transitions**:
```
[Created] --> [Ready] --> [Deleted]
     |           |
     v           v
  [Failed]   [Updating]
                 |
                 v
             [Ready]
```

---

### 2. UploadJob

Represents an in-progress or completed CSV upload and ingestion job.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | string (UUID) | Primary key, auto-generated | Unique job identifier |
| database_id | string (UUID) | Foreign key to VectorDatabase | Target database |
| filename | string | Non-empty | Original uploaded filename |
| file_size_bytes | integer | > 0, <= 104857600 (100MB) | File size in bytes |
| content_column | string | Non-empty | CSV column to embed |
| id_column | string | Optional | CSV column for document IDs |
| metadata_columns | string[] | Optional | Additional columns to store |
| status | enum | pending, processing, completed, failed | Current job status |
| progress_percent | integer | 0-100 | Processing progress |
| documents_processed | integer | >= 0 | Number of documents processed |
| documents_failed | integer | >= 0 | Number of documents that failed |
| error_message | string | Optional | Error details if failed |
| started_at | datetime | Optional | Processing start time |
| completed_at | datetime | Optional | Processing completion time |
| created_at | datetime | Auto-set | Job creation timestamp |

**State Transitions**:
```
[Pending] --> [Processing] --> [Completed]
                   |
                   v
               [Failed]
```

---

### 3. SearchQuery

Represents a search request against one or more databases.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | string (UUID) | Auto-generated | Query identifier (for logging) |
| query_type | enum | text, image | Type of search query |
| query_content | string | Non-empty | Text query or base64 image data |
| database_ids | string[] | 1-4 items | Target databases to search |
| limit | integer | 1-100, default 10 | Max results per database |
| min_score | float | 0.0-1.0, optional | Minimum similarity threshold |
| created_at | datetime | Auto-set | Query timestamp |

**Validation Rules**:
- `database_ids` must contain 1-4 valid database IDs
- For `query_type: image`, `query_content` must be valid base64
- `limit` defaults to 10 if not specified

---

### 4. SearchResult

Represents a single result from a vector search.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | string | Non-empty | Document ID from the database |
| content | string | Non-empty | Document content text |
| score | float | 0.0-1.0 | Similarity score (higher = more similar) |
| metadata | object | Optional | Additional document metadata |
| database_id | string (UUID) | Non-empty | Source database identifier |
| database_name | string | Non-empty | Source database display name |

---

### 5. SearchResponse

Aggregated response for a search query across multiple databases.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| query_id | string (UUID) | Non-empty | Reference to SearchQuery |
| results | Map<string, SearchResult[]> | Keyed by database_id | Results grouped by database |
| total_results | integer | >= 0 | Total results across all databases |
| query_time_ms | integer | >= 0 | Total query execution time |

---

## Relationships

```
┌─────────────────┐       ┌─────────────────┐
│ VectorDatabase  │ 1───* │   UploadJob     │
│                 │       │                 │
│ - id            │       │ - database_id   │
│ - name          │       │ - status        │
│ - document_count│       │ - progress      │
└─────────────────┘       └─────────────────┘
        │
        │ 1
        │
        * (searched by)
        │
┌─────────────────┐       ┌─────────────────┐
│  SearchQuery    │ 1───* │  SearchResult   │
│                 │       │                 │
│ - database_ids  │       │ - database_id   │
│ - query_type    │       │ - score         │
└─────────────────┘       └─────────────────┘
```

---

## Enumerations

### DatabaseStatus
```
CREATING   - Database is being created
READY      - Database is ready for use
UPDATING   - Database is being updated (re-ingestion)
DELETING   - Database is being deleted
FAILED     - Database creation/update failed
```

### UploadStatus
```
PENDING    - Upload received, waiting to process
PROCESSING - Currently processing CSV
COMPLETED  - Processing finished successfully
FAILED     - Processing failed with error
```

### QueryType
```
TEXT       - Natural language text query
IMAGE      - Image-based query (base64 encoded)
```

---

## Database Schema (SQLite)

```sql
-- Vector database metadata
CREATE TABLE vector_databases (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    collection_name TEXT UNIQUE NOT NULL,
    document_count INTEGER DEFAULT 0,
    embedding_model TEXT NOT NULL,
    embedding_dimension INTEGER NOT NULL,
    status TEXT DEFAULT 'CREATING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Upload job tracking
CREATE TABLE upload_jobs (
    id TEXT PRIMARY KEY,
    database_id TEXT NOT NULL REFERENCES vector_databases(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    content_column TEXT NOT NULL,
    id_column TEXT,
    metadata_columns TEXT,  -- JSON array
    status TEXT DEFAULT 'PENDING',
    progress_percent INTEGER DEFAULT 0,
    documents_processed INTEGER DEFAULT 0,
    documents_failed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_upload_jobs_database_id ON upload_jobs(database_id);
CREATE INDEX idx_upload_jobs_status ON upload_jobs(status);
CREATE INDEX idx_vector_databases_name ON vector_databases(name);
```

---

## Pydantic Schemas (Backend)

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import re

class DatabaseStatus(str, Enum):
    CREATING = "CREATING"
    READY = "READY"
    UPDATING = "UPDATING"
    DELETING = "DELETING"
    FAILED = "FAILED"

class UploadStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class QueryType(str, Enum):
    TEXT = "text"
    IMAGE = "image"

class VectorDatabaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9 -]*[a-zA-Z0-9]$', v) and len(v) > 1:
            raise ValueError('Name must be alphanumeric with spaces/hyphens')
        return v

class VectorDatabaseResponse(BaseModel):
    id: str
    name: str
    collection_name: str
    document_count: int
    embedding_model: str
    embedding_dimension: int
    status: DatabaseStatus
    created_at: datetime
    updated_at: datetime

class SearchRequest(BaseModel):
    database_ids: list[str] = Field(..., min_length=1, max_length=4)
    query_type: QueryType
    query_content: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    min_score: float | None = Field(default=None, ge=0.0, le=1.0)

class SearchResultItem(BaseModel):
    id: str
    content: str
    score: float
    metadata: dict | None = None
    database_id: str
    database_name: str

class SearchResponse(BaseModel):
    query_id: str
    results: dict[str, list[SearchResultItem]]
    total_results: int
    query_time_ms: int
```

---

## TypeScript Types (Frontend)

```typescript
// Enums
type DatabaseStatus = 'CREATING' | 'READY' | 'UPDATING' | 'DELETING' | 'FAILED';
type UploadStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
type QueryType = 'text' | 'image';

// Entities
interface VectorDatabase {
  id: string;
  name: string;
  collectionName: string;
  documentCount: number;
  embeddingModel: string;
  embeddingDimension: number;
  status: DatabaseStatus;
  createdAt: string;  // ISO datetime
  updatedAt: string;
}

interface UploadJob {
  id: string;
  databaseId: string;
  filename: string;
  fileSizeBytes: number;
  contentColumn: string;
  idColumn?: string;
  metadataColumns?: string[];
  status: UploadStatus;
  progressPercent: number;
  documentsProcessed: number;
  documentsFailed: number;
  errorMessage?: string;
  startedAt?: string;
  completedAt?: string;
  createdAt: string;
}

interface SearchResult {
  id: string;
  content: string;
  score: number;
  metadata?: Record<string, unknown>;
  databaseId: string;
  databaseName: string;
}

interface SearchResponse {
  queryId: string;
  results: Record<string, SearchResult[]>;
  totalResults: number;
  queryTimeMs: number;
}

// Request types
interface CreateDatabaseRequest {
  name: string;
}

interface SearchRequest {
  databaseIds: string[];
  queryType: QueryType;
  queryContent: string;
  limit?: number;
  minScore?: number;
}

interface UploadRequest {
  file: File;
  databaseName: string;
  contentColumn: string;
  idColumn?: string;
  metadataColumns?: string[];
}
```

# Research: Web GUI for Vector Database Management

**Feature**: 002-web-gui  
**Date**: 2024-12-17  
**Status**: Complete

## Overview

This document consolidates research findings for building a web-based GUI for vector database management. The system integrates with the existing `vetorizer_lib` library and uses Qdrant as the vector database backend.

---

## 1. Backend Framework Selection

### Decision: FastAPI

**Rationale**:
- Native async support for handling concurrent file uploads and search requests
- Automatic OpenAPI documentation generation
- Pydantic integration for request/response validation
- Excellent performance for I/O-bound operations
- Strong typing support aligns with constitution requirements
- Easy integration with existing Python `vetorizer_lib`

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Flask | No native async, manual OpenAPI setup required |
| Django | Too heavyweight for API-only backend, slower for simple CRUD |
| Starlette | Lower-level, FastAPI provides better DX with same performance |

**Best Practices**:
- Use dependency injection for services (vetorizer_lib client)
- Implement proper error handling with HTTPException
- Use BackgroundTasks for long-running operations (CSV ingestion)
- Configure CORS for frontend communication

---

## 2. Frontend Framework Selection

### Decision: React + Vite + TailwindCSS

**Rationale**:
- React: Industry standard, large ecosystem, component-based architecture
- Vite: Fast development server, optimized production builds
- TailwindCSS: Utility-first CSS, rapid UI development, consistent design
- TypeScript: Type safety aligns with constitution requirements

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Vue.js | Smaller ecosystem, less familiar to most developers |
| Next.js | SSR not needed for this SPA, adds complexity |
| Angular | Steeper learning curve, heavier framework |
| Svelte | Smaller ecosystem, less mature tooling |

**UI Component Strategy**:
- Use shadcn/ui for pre-built accessible components
- Lucide React for consistent iconography
- React Query (TanStack Query) for server state management
- React Router for client-side routing

---

## 3. File Upload Handling

### Decision: Chunked Upload with Progress Tracking

**Rationale**:
- Support for large files (up to 100MB per spec)
- Real-time progress feedback to users
- Resumable uploads for reliability
- Server-side validation before processing

**Implementation Approach**:
```
Frontend:
- Use native File API with progress events
- Display upload progress bar
- Validate file type/size before upload

Backend:
- FastAPI UploadFile with streaming
- Temporary file storage during upload
- Background task for CSV processing
- WebSocket or SSE for progress updates
```

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Base64 encoding | Memory inefficient for large files |
| Direct multipart | No progress tracking without chunking |
| Third-party upload service | Adds external dependency |

---

## 4. Progress Updates for Long Operations

### Decision: Server-Sent Events (SSE)

**Rationale**:
- Simpler than WebSockets for one-way server-to-client updates
- Native browser support, no additional libraries needed
- Automatic reconnection handling
- Sufficient for progress updates (no bidirectional communication needed)

**Implementation**:
- FastAPI StreamingResponse for SSE endpoint
- EventSource API on frontend
- Progress events: `started`, `progress`, `completed`, `error`

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| WebSockets | Overkill for one-way updates, more complex |
| Polling | Inefficient, higher latency |
| Long polling | More complex than SSE, similar limitations |

---

## 5. Database Metadata Storage

### Decision: SQLite for Metadata

**Rationale**:
- Lightweight, no separate server process
- Perfect for storing database metadata (names, creation dates, document counts)
- File-based persistence aligns with single-server deployment
- Easy backup and migration

**Schema Design**:
```sql
CREATE TABLE vector_databases (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    collection_name TEXT NOT NULL,
    document_count INTEGER DEFAULT 0,
    embedding_model TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| JSON file | No query capability, concurrent access issues |
| PostgreSQL | Overkill for metadata, requires separate server |
| Qdrant metadata | Not designed for relational queries |

---

## 6. Qdrant Integration Strategy

### Decision: Use vetorizer_lib with Multiple Collections

**Rationale**:
- Each named database maps to a Qdrant collection
- Leverage existing vetorizer_lib for embedding and storage
- Collection names derived from user-provided database names
- File-based Qdrant persistence for data durability

**Implementation**:
- VetorizerClient instance per database operation
- Collection name = sanitized database name (alphanumeric + hyphens)
- Qdrant path configured in backend settings
- Support for both in-memory (testing) and file-based (production) modes

**Collection Naming Convention**:
```python
def sanitize_collection_name(name: str) -> str:
    """Convert user database name to valid Qdrant collection name."""
    # Replace spaces with hyphens, remove special chars, lowercase
    return re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-'))
```

---

## 7. Search Implementation

### Decision: Unified Search Interface with Mode Selection

**Rationale**:
- Single search endpoint handles both text and image queries
- Query type determined by request content
- Consistent response format regardless of query type
- Supports comparison across multiple databases

**API Design**:
```
POST /api/search
{
    "databases": ["db1", "db2"],  // 1-4 databases
    "query_type": "text" | "image",
    "query": "search text" | base64_image_data,
    "limit": 10,
    "min_score": 0.5
}
```

**Response**:
```
{
    "results": {
        "db1": [{ "id", "content", "score", "metadata" }],
        "db2": [{ "id", "content", "score", "metadata" }]
    },
    "query_time_ms": 150
}
```

---

## 8. Frontend State Management

### Decision: React Query + React Context

**Rationale**:
- React Query handles server state (databases, search results)
- React Context for UI state (selected databases, comparison mode)
- Automatic caching and background refetching
- Optimistic updates for better UX

**State Categories**:
| Category | Solution | Examples |
|----------|----------|----------|
| Server State | React Query | Database list, search results |
| UI State | React Context | Selected databases, active tab |
| Form State | React Hook Form | Upload form, search form |
| URL State | React Router | Current page, query params |

---

## 9. Error Handling Strategy

### Decision: Structured Error Responses

**Backend Error Format**:
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Human-readable message",
        "details": { "field": "specific issue" }
    }
}
```

**Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid input data |
| NOT_FOUND | 404 | Database or resource not found |
| DUPLICATE_NAME | 409 | Database name already exists |
| FILE_TOO_LARGE | 413 | Upload exceeds 100MB limit |
| PROCESSING_ERROR | 500 | Embedding or storage failure |

**Frontend Handling**:
- Toast notifications for transient errors
- Inline validation for form errors
- Error boundaries for unexpected failures
- Retry logic for network errors

---

## 10. Testing Strategy

### Backend Testing:
- **Unit Tests**: Service layer with mocked vetorizer_lib
- **Integration Tests**: API endpoints with test database
- **Contract Tests**: OpenAPI schema validation

### Frontend Testing:
- **Unit Tests**: Component rendering with React Testing Library
- **Integration Tests**: User flows with MSW for API mocking
- **E2E Tests**: Critical paths with Playwright (optional)

**Test Database Strategy**:
- In-memory Qdrant for fast tests
- Isolated SQLite database per test
- Fixtures for common test data

---

## 11. Security Considerations

### Decisions:
- **CORS**: Restrict to frontend origin in production
- **File Validation**: Check MIME type and file extension
- **Input Sanitization**: Validate all user inputs
- **Rate Limiting**: Prevent abuse of upload/search endpoints
- **No Authentication**: Single-user local deployment (per spec assumptions)

**Future Considerations** (out of scope):
- Multi-user authentication
- API key management
- Role-based access control

---

## 12. Deployment Strategy

### Decision: Single Docker Compose Setup

**Rationale**:
- Simple deployment for single-server scenario
- Backend and frontend in separate containers
- Shared volume for Qdrant data persistence
- Easy local development with docker-compose

**Container Structure**:
```yaml
services:
  backend:
    build: ./web/backend
    volumes:
      - qdrant_data:/data/qdrant
      - sqlite_data:/data/sqlite
    ports:
      - "8000:8000"
  
  frontend:
    build: ./web/frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

---

## Summary

All technical decisions align with:
- Constitution requirements (type safety, testing, documentation)
- Spec requirements (performance, usability, features)
- User input (Qdrant as vector database, graphical interface)

No NEEDS CLARIFICATION items remain. Ready for Phase 1: Design & Contracts.

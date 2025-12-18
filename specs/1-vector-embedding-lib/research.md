# Research: Vector Embedding Library

**Feature**: 1-vector-embedding-lib  
**Date**: 2025-12-17  
**Status**: Complete

## Research Areas

### 1. Embedding Model Selection

**Decision**: Use `sentence-transformers` library for text embeddings, `transformers` + CLIP for image embeddings

**Rationale**:
- sentence-transformers provides optimized, production-ready sentence embeddings
- Built on top of HuggingFace transformers with simpler API
- Supports 100+ pre-trained models with consistent interface
- CLIP (via transformers) enables text-image cross-modal search

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Raw transformers only | More complex API, requires manual pooling |
| OpenAI embeddings | Requires API key, not self-hosted, cost per request |
| Cohere embeddings | Same issues as OpenAI |
| FastEmbed | Less model variety, newer/less tested |

**Default Models**:
- Text: `sentence-transformers/all-MiniLM-L6-v2` (384 dims, fast, good quality)
- Image/Multimodal: `openai/clip-vit-base-patch32` (512 dims)

---

### 2. Vector Database Client

**Decision**: Use `qdrant-client` official Python SDK

**Rationale**:
- Official client maintained by Qdrant team
- Supports both sync and async operations
- Handles batching, retries, and connection pooling
- Works with local (in-memory, file) and cloud Qdrant

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Raw HTTP requests | Reinventing the wheel, no retry logic |
| chromadb | Different API, user specified Qdrant |
| pinecone | Proprietary, requires account |
| weaviate | Different system, user specified Qdrant |

**Connection Patterns**:
- Local development: `QdrantClient(":memory:")` or `QdrantClient(path="./qdrant_data")`
- Production: `QdrantClient(url="http://localhost:6333")` or cloud URL with API key

---

### 3. CSV Processing Strategy

**Decision**: Use `pandas` with chunked reading for memory-bounded ingestion

**Rationale**:
- pandas is the de-facto standard for CSV handling in Python
- `read_csv(chunksize=N)` enables streaming large files
- Handles encoding, missing values, type inference
- Familiar API for Python developers

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| csv module (stdlib) | No chunking, manual type handling |
| polars | Faster but less familiar, adds dependency |
| dask | Overkill for single-file processing |

**Batch Processing**:
- Default batch size: 100 documents per embedding call
- Configurable via `IngestConfig.batch_size`
- Progress reporting via callback or tqdm integration

---

### 4. Dependency Injection Pattern

**Decision**: Constructor injection with protocol-based abstractions

**Rationale**:
- Aligns with Constitution Principle I (testability, DI)
- Protocols (typing.Protocol) enable duck typing without inheritance
- Easy to mock for unit tests
- Supports swapping implementations (e.g., different vector stores)

**Pattern**:
```python
class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...

class VectorStore(Protocol):
    def upsert(self, documents: list[Document]) -> None: ...
    def search(self, vector: list[float], limit: int) -> list[SearchResult]: ...

class VetorizerClient:
    def __init__(self, embedder: Embedder, store: VectorStore) -> None:
        self._embedder = embedder
        self._store = store
```

---

### 5. Error Handling Strategy

**Decision**: Custom exception hierarchy with actionable messages

**Rationale**:
- Constitution requires clear error messages (FR-009)
- Specific exceptions enable targeted error handling
- Messages include cause and suggested resolution

**Exception Hierarchy**:
```
VetorizerError (base)
├── ConfigurationError      # Invalid config, missing params
├── ConnectionError         # Qdrant unreachable
├── ModelLoadError          # HuggingFace model issues
├── IngestError             # CSV/data processing failures
└── SearchError             # Query execution failures
```

---

### 6. uv Project Setup

**Decision**: Standard uv project with pyproject.toml

**Rationale**:
- User specified uv as package manager
- pyproject.toml is PEP 621 standard
- uv.lock ensures reproducible builds

**Project Configuration**:
```toml
[project]
name = "vetorizer-lib"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "sentence-transformers>=2.2.0",
    "qdrant-client>=1.7.0",
    "transformers>=4.35.0",
    "torch>=2.0.0",
    "pandas>=2.0.0",
    "Pillow>=10.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
]
```

---

### 7. Testing Strategy

**Decision**: pytest with fixtures for mocked and real integrations

**Rationale**:
- Constitution requires TDD with unit/integration/contract tests
- pytest is Python standard, good fixture support
- pytest-asyncio for async Qdrant operations

**Test Categories**:
| Category | Scope | Dependencies |
|----------|-------|--------------|
| Unit | Embedders, models, config | Mocked |
| Integration | Full client with real Qdrant | Docker/local Qdrant |
| Contract | Public API stability | None |

**Fixtures**:
- `mock_embedder`: Returns deterministic vectors
- `mock_store`: In-memory dict-based store
- `qdrant_client`: Real Qdrant (integration only)

---

## Resolved Clarifications

All technical decisions have been made. No NEEDS CLARIFICATION items remain.

## Next Steps

1. Generate data-model.md with entity definitions
2. Generate contracts/api.md with public API
3. Generate quickstart.md with usage examples

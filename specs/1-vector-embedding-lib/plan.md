# Implementation Plan: Vector Embedding Library

**Branch**: `1-vector-embedding-lib` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-vector-embedding-lib/spec.md`

## Summary

A Python library for embedding text and images using HuggingFace models and storing them in Qdrant vector database. Core features: CSV data ingestion with batch processing, semantic search with similarity scoring, configurable embedding models (sentence-transformers for text, CLIP for images). Built with uv for modern Python package management.

## Technical Context

**Language/Version**: Python 3.10+ (uv-managed)  
**Package Manager**: uv (pyproject.toml, uv.lock)  
**Primary Dependencies**: sentence-transformers, qdrant-client, transformers, torch, Pillow, pandas  
**Storage**: Qdrant vector database (local or cloud)  
**Testing**: pytest with pytest-asyncio, pytest-cov  
**Target Platform**: Cross-platform (Linux, macOS, Windows)  
**Project Type**: Single library package  
**Performance Goals**: 10K rows ingested in <5 min, search <500ms for 100K vectors  
**Constraints**: Memory-bounded ingestion (streaming/batching), <200ms p95 search  
**Scale/Scope**: Up to 100K vectors, single-node Qdrant

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status |
|-----------|-------------|--------|
| I. Code Quality | Single responsibility, DI, pure functions, type hints (mypy/pyright) | ✅ Will comply |
| I. Type Hinting | ALL parameters and returns typed, no `Any` without justification | ✅ Will comply |
| II. Testing | Test-first (TDD), unit + integration + contract tests, <100ms unit tests | ✅ Will comply |
| III. UX Consistency | N/A (library, not UI) | ✅ N/A |
| IV. Performance | <200ms p95 search, bounded memory, no blocking main thread | ✅ Will comply |
| V. Documentation | README with install/example, Google-style docstrings, CHANGELOG | ✅ Will comply |
| V. uv Integration | Document `uv sync`, `uv run`, `uv add` workflows | ✅ Will comply |

**Gate Status**: ✅ PASS - No violations

## Project Structure

### Documentation (this feature)

```text
specs/1-vector-embedding-lib/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.md           # Public API contract
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
vetorizer_lib/
├── __init__.py          # Public API exports
├── client.py            # Main VetorizerClient class
├── models/
│   ├── __init__.py
│   ├── embedding.py     # EmbeddingModel abstraction
│   ├── document.py      # Document and SearchResult
│   └── config.py        # Configuration dataclasses
├── embedders/
│   ├── __init__.py
│   ├── base.py          # Abstract embedder interface
│   ├── text.py          # SentenceTransformer embedder
│   └── image.py         # CLIP embedder
├── stores/
│   ├── __init__.py
│   ├── base.py          # Abstract vector store interface
│   └── qdrant.py        # Qdrant implementation
├── ingest/
│   ├── __init__.py
│   └── csv.py           # CSV ingestion with batching
└── exceptions.py        # Custom exceptions

tests/
├── conftest.py          # Shared fixtures
├── unit/
│   ├── test_embedders.py
│   ├── test_models.py
│   └── test_ingest.py
├── integration/
│   ├── test_qdrant.py
│   └── test_client.py
└── contract/
    └── test_api.py

pyproject.toml           # uv project config
uv.lock                  # Locked dependencies
README.md                # Entry point documentation
CHANGELOG.md             # Release history
```

**Structure Decision**: Single library package following Python conventions. Source in `vetorizer_lib/` (underscore for valid Python package name), tests in `tests/` with unit/integration/contract separation per constitution.

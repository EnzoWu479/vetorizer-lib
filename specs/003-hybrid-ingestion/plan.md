# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable hybrid ingestion mode that combines text and image embeddings through vector concatenation. Users can select ingestion mode (text-only, image-only, or hybrid) when creating databases via the web UI. All modes start with CSV upload: text mode processes CSV with (text, label) columns, image mode processes CSV with (image_path, label) columns, and hybrid mode processes CSV referencing documents/images/PDFs containing both modalities. The system validates files, creates databases, and performs ingestion in a single transactional operation.

## Technical Context

**Language/Version**: Python 3.10+ (uv-managed)  
**Primary Dependencies**: FastAPI, Jinja2, HTMX, Tailwind CSS (CDN), sentence-transformers, transformers, torch, Pillow, qdrant-client  
**Storage**: Qdrant vector database (file-based or remote) for vectors AND metadata  
**Testing**: pytest with pytest-asyncio, pytest-cov  
**Target Platform**: Modern web browsers + Python backend (cross-platform: Linux, macOS, Windows)  
**Project Type**: Web application (Python library with integrated web UI, CLI-launchable)  
**Performance Goals**: <2s search response, <3min CSV ingestion for 10K rows, <200ms API p95  
**Constraints**: 100MB max CSV upload, 10 concurrent users, deterministic vector concatenation  
**Scale/Scope**: Single-server deployment, up to 100K documents per database, 3 ingestion modes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality & Testability | PASS | Type hints required, dependency injection pattern, modular embedder system |
| II. Testing Standards | PASS | TDD approach with unit + integration + contract tests, test CSV fixtures for all modes |
| III. User Experience Consistency | PASS | HTMX + Tailwind UI, clear mode selection, inline help text, validation feedback |
| IV. Performance Requirements | PASS | <200ms p95 API, <3min ingestion for 10K rows, streaming/batching for memory efficiency |
| V. Documentation Standards | PASS | Google-style docstrings, inline CSV format help, mode-specific examples |

**Quality Gates**:
- Linting: ruff (Python)
- Type Safety: mypy with strict mode
- Testing: pytest with coverage >80%
- Documentation: All public APIs and UI flows documented
- Validation: Pre-ingest file validation with detailed feedback

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
vetorizer_lib/
├── __init__.py              # Existing - exports client
├── client.py                # EXISTING - VetorizerClient (may need updates)
├── exceptions.py            # EXISTING
├── embedders/               # EXISTING - UPDATE for hybrid mode
│   ├── __init__.py
│   ├── base.py              # BaseEmbedder interface
│   ├── text.py              # TextEmbedder (sentence-transformers)
│   └── image.py             # ImageEmbedder (CLIP)
├── models/                  # EXISTING - ADD HybridVector model
│   ├── __init__.py
│   ├── config.py            # Configuration models
│   ├── document.py          # Document model
│   └── hybrid.py            # NEW: HybridVector, IngestMode enum
├── ingest/                  # EXISTING - UPDATE for hybrid ingestion
│   ├── __init__.py
│   └── csv.py               # CSV ingestion with mode selection
├── stores/                  # EXISTING
│   ├── __init__.py
│   ├── base.py              # VectorStore interface
│   └── qdrant.py            # QdrantVectorStore implementation
└── web/                     # EXISTING WEB UI
    ├── __init__.py
    ├── app.py               # FastAPI app
    ├── cli.py               # CLI entry point
    ├── config.py            # Web settings
    ├── deps.py              # Dependency injection
    ├── routes/              # API routes
    │   ├── __init__.py
    │   ├── databases.py     # UPDATE: Add validation endpoint
    │   ├── upload.py        # UPDATE: Handle hybrid ingestion
    │   ├── search.py        # UPDATE: Support hybrid search
    │   └── config.py        # Config endpoints
    ├── services/            # Business logic
    │   ├── __init__.py
    │   ├── database_service.py  # UPDATE: Create with mode
    │   ├── upload_service.py    # UPDATE: Mode-aware ingestion
    │   └── search_service.py    # UPDATE: Hybrid search
    ├── models/              # Web-specific models
    │   ├── __init__.py
    │   ├── schemas.py       # UPDATE: Add IngestMode, validation responses
    │   └── metadata_store.py
    ├── templates/           # Jinja2 templates
    │   ├── base.html        # EXISTING
    │   ├── index.html       # EXISTING
    │   ├── search.html      # UPDATE: Hybrid search UI
    │   └── partials/
    │       ├── create_database_modal.html  # EXISTING - UPDATED for CSV-only + mode descriptions
    │       └── [other partials]
    ├── static/              # Static assets
    │   ├── css/
    │   │   └── styles.css   # Tailwind customizations
    │   └── js/
    │       ├── htmx.min.js
    │       └── create_database_modal.js  # EXISTING - UPDATE validation logic
    └── [other web files]

tests/
├── conftest.py              # EXISTING - ADD hybrid fixtures
├── unit/
│   ├── test_embedders.py    # EXISTING
│   ├── test_models.py       # UPDATE: Test HybridVector
│   ├── test_hybrid_vector.py # NEW: Hybrid concatenation tests
│   ├── test_ingest.py       # UPDATE: Mode-specific ingestion
│   └── web/
│       └── [web unit tests] # UPDATE: Modal, validation
├── integration/
│   ├── test_qdrant.py       # EXISTING
│   ├── test_client_hybrid_ingest.py  # NEW: End-to-end hybrid ingestion
│   └── web/
│       └── [web integration tests]  # UPDATE: Full flow tests
└── contract/
    └── test_api.py          # UPDATE: New validation endpoint

pyproject.toml               # EXISTING - dependencies already in place
README.md                    # UPDATE: Document hybrid mode
CHANGELOG.md                 # UPDATE: Add 003-hybrid-ingestion entry
```

**Structure Decision**: Integrated Python web application extending existing vetorizer_lib. Uses FastAPI + Jinja2 + HTMX + Tailwind CSS for UI. Hybrid ingestion extends existing embedder system with concatenation strategy. All ingestion modes start with CSV upload following domain-specific column structure.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

# Implementation Plan: Ingestão Híbrida (Texto/Imagem)

**Branch**: `003-hybrid-ingestion` | **Date**: 2025-12-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-hybrid-ingestion/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable hybrid (text + image) ingestion by allowing users to create databases via UI home page with mode selection (text only / image only / hybrid). System generates hybrid vectors by concatenating text and image embeddings deterministically. UI provides modal/form for database creation with name, mode selection (radio buttons), file upload, and advanced embedder configuration (collapsible). Validation summary shows detailed file status before proceeding. Single-step operation creates database and ingests documents transactionally.

## Technical Context

**Language/Version**: Python 3.10+ (>=3.10 per pyproject.toml)  
**Primary Dependencies**: FastAPI (web framework), sentence-transformers (text embeddings), transformers (CLIP models), Pillow (image processing), qdrant-client (vector storage), Jinja2 (templates), HTMX (dynamic UI)  
**Storage**: Qdrant vector database (file-based persistence for vectors and metadata)  
**Testing**: pytest with pytest-asyncio, pytest-cov  
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge), cross-platform server (Linux, macOS, Windows)  
**Project Type**: Python library with integrated web UI (single project structure)  
**Performance Goals**: <2s search response, <3min CSV ingestion for 10K rows, <200ms API p95  
**Constraints**: 100MB max file upload, 10 concurrent users, memory-bounded ingestion  
**Scale/Scope**: Single-server deployment, up to 100K documents per database, 100+ documents per upload batch

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality & Testability | PASS | Type hints required on all functions (text/image embedder integration, hybrid vector concatenation). Dependency injection for embedder models. Pure functions for vector concatenation logic. |
| II. Testing Standards | PASS | TDD approach mandatory. Unit tests for hybrid vector concatenation, validation logic. Integration tests for end-to-end database creation + upload. Contract tests for new API endpoints. |
| III. User Experience Consistency | PASS | Modal/form follows existing UI patterns. Radio buttons for mode selection aligns with web standards. Validation summary with detailed feedback matches constitution requirements. Loading indicators for upload/processing. |
| IV. Performance Requirements | PASS | <200ms API p95 maintained. File validation before processing prevents wasted computation. Progress indicators for uploads. Batched processing for documents. |
| V. Documentation Standards | PASS | Google-style docstrings for all new functions. README updated with hybrid ingestion examples. API endpoints documented in OpenAPI schema. |

**Quality Gates**:
- Linting: ruff (Python) - all new code must pass
- Type Safety: mypy (Python) - strict mode with no `Any` types
- Testing: pytest with >90% coverage for new code
- Documentation: All public APIs documented with examples

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
├── __init__.py                    # Existing - may need hybrid exports
├── client.py                      # Existing - EXTEND for hybrid mode
├── models/
│   ├── __init__.py               # Existing
│   ├── hybrid.py                 # EXISTING - HybridVector class
│   ├── config.py                 # Existing - may need hybrid config
│   └── document.py               # Existing
├── embedders/
│   ├── __init__.py               # Existing
│   ├── base.py                   # Existing
│   ├── text.py                   # Existing - TextEmbedder
│   └── image.py                  # Existing - ImageEmbedder
├── ingest/
│   ├── __init__.py               # Existing
│   └── csv.py                    # EXTEND for hybrid ingestion
├── web/
│   ├── __init__.py               # Existing
│   ├── app.py                    # Existing
│   ├── models/
│   │   ├── __init__.py           # Existing
│   │   ├── schemas.py            # EXTEND - add CreateDatabaseRequest, ValidationSummary
│   │   └── metadata_store.py    # EXTEND - add hybrid mode support
│   ├── routes/
│   │   ├── __init__.py           # Existing
│   │   ├── databases.py          # EXTEND - add create endpoint with hybrid support
│   │   ├── upload.py             # EXTEND - hybrid validation logic
│   │   └── search.py             # EXTEND - hybrid search support
│   ├── services/
│   │   ├── __init__.py           # Existing
│   │   ├── database_service.py   # EXTEND - hybrid database creation
│   │   └── upload_service.py     # EXTEND - hybrid file validation
│   ├── templates/
│   │   ├── index.html            # EXTEND - add "Create Database" button/modal
│   │   └── partials/
│   │       └── create_database_modal.html  # NEW - database creation form
│   └── static/
│       ├── css/
│       │   └── styles.css        # EXTEND - modal styling
│       └── js/
│           └── htmx.min.js       # Existing

tests/
├── unit/
│   ├── test_hybrid_vector.py        # EXISTING - may need expansion
│   ├── test_client_hybrid_ingest.py # EXISTING - expand for new modes
│   └── web/
│       ├── test_database_service.py # NEW - database creation logic
│       └── test_validation.py       # NEW - file validation logic
├── integration/
│   └── web/
│       ├── test_create_database.py  # NEW - end-to-end database creation
│       └── test_hybrid_upload.py    # NEW - hybrid upload workflow
└── contract/
    └── test_api.py                   # EXTEND - new database creation endpoints
```

**Structure Decision**: Single Python library with integrated web UI. Extends existing vetorizer_lib structure with hybrid ingestion capabilities. Focus on:
- **Core layer**: HybridVector already exists, extend CSV ingestion and client
- **Web layer**: New UI modal, extend routes/services for database creation
- **Tests**: New test files for database creation workflow, extend existing contract tests

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

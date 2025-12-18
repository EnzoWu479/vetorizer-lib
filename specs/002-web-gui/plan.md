# Implementation Plan: Web GUI for Vector Database Management

**Branch**: `002-web-gui` | **Date**: 2024-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-web-gui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a web-based graphical interface that enables users to:
1. Upload CSV files and create named vector databases using Qdrant
2. Search databases using text or image queries
3. Compare search results across multiple databases side-by-side
4. Manage (list, rename, delete) vector databases

The system will be integrated into the existing `vetorizer_lib` Python library, using FastAPI to serve both the API and HTML templates with HTMX for dynamic interactions. Users launch the web UI via CLI command.

## Technical Context

**Language/Version**: Python 3.10+ (single language for entire application)  
**Primary Dependencies**: FastAPI (API + static file serving), Jinja2 (HTML templates), HTMX (dynamic UI), vetorizer_lib (embedding/storage)  
**Storage**: Qdrant vector database (file-based persistence) for both vectors AND metadata (no SQLite)  
**Testing**: pytest (all tests)  
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge)  
**Project Type**: Python library with integrated web UI (CLI-launchable)  
**Performance Goals**: <2s search response, <3min CSV ingestion for 10K rows  
**Constraints**: 100MB max file upload, 10 concurrent users, <200ms API p95  
**Scale/Scope**: Single-server deployment, up to 100K documents per database  
**CLI Launch**: `python -m vetorizer_lib serve` or `vetorizer serve`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality & Testability | PASS | Type hints required, dependency injection for vetorizer_lib |
| II. Testing Standards | PASS | TDD approach, unit + integration + contract tests |
| III. User Experience Consistency | PASS | Jinja2 templates + HTMX + TailwindCSS, loading states, error handling |
| IV. Performance Requirements | PASS | <200ms API p95, <2s search, progress indicators for uploads |
| V. Documentation Standards | PASS | Google-style docstrings, README with examples |

**Quality Gates**:
- Linting: ruff (Python)
- Type Safety: mypy (Python)
- Testing: pytest with coverage thresholds
- Documentation: All public APIs documented

## Project Structure

### Documentation (this feature)

```text
specs/002-web-gui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI spec)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
vetorizer_lib/
├── __init__.py              # Existing - add web exports
├── client.py                # Existing VetorizerClient
├── exceptions.py            # Existing exceptions
├── web/                     # NEW: Web UI module
│   ├── __init__.py
│   ├── app.py               # FastAPI application
│   ├── cli.py               # CLI entry point (serve command)
│   ├── config.py            # Web-specific settings
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── databases.py     # Database CRUD endpoints
│   │   ├── search.py        # Search endpoints
│   │   └── upload.py        # CSV upload endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database_service.py
│   │   ├── search_service.py
│   │   └── upload_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py       # Pydantic schemas for web
│   │   └── metadata_store.py # Qdrant-based metadata storage (replaces SQLite)
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html        # Base layout with HTMX
│   │   ├── index.html       # Home/upload page
│   │   ├── search.html      # Search page
│   │   ├── compare.html     # Comparison page
│   │   ├── manage.html      # Database management page
│   │   └── partials/        # HTMX partial templates
│   │       ├── database_list.html
│   │       ├── search_results.html
│   │       ├── upload_progress.html
│   │       └── comparison_results.html
│   └── static/              # Static assets
│       ├── css/
│       │   └── styles.css   # TailwindCSS compiled
│       └── js/
│           └── htmx.min.js  # HTMX library

tests/
├── unit/
│   └── web/                 # Web module unit tests
├── integration/
│   └── web/                 # Web integration tests
└── contract/
    └── web/                 # Web API contract tests
```

**Structure Decision**: Integrated Python architecture with web UI as a submodule of vetorizer_lib. Uses FastAPI for API + static serving, Jinja2 for HTML templates, and HTMX for dynamic interactions. CLI command launches the web server. Qdrant is used as the vector database per user requirement.

## Complexity Tracking

> No constitution violations requiring justification.

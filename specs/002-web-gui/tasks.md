# Implementation Tasks: Web GUI for Vector Database Management

**Feature**: 002-web-gui  
**Branch**: `002-web-gui`  
**Date**: 2024-12-17  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Overview

This document contains all implementation tasks organized by user story priority. Each phase is independently testable and delivers incremental value.

**Architecture**: Python-only, integrated into vetorizer_lib, CLI-launchable web UI using FastAPI + Jinja2 + HTMX.

**User Stories**:
- **US1** (P1): Upload CSV and Create Named Vector Database
- **US2** (P2): Search Vector Database by Text
- **US3** (P3): Search by Image
- **US4** (P4): Compare Search Results Across Databases
- **US5** (P5): Manage Vector Databases

---

## Phase 1: Setup

**Goal**: Initialize web module structure within vetorizer_lib

- [x] T001 Create vetorizer_lib/web/ directory structure per plan.md
- [x] T002 Add web dependencies to pyproject.toml (fastapi, uvicorn, jinja2, python-multipart, aiosqlite, sse-starlette)
- [x] T003 [P] Create vetorizer_lib/web/__init__.py with module exports
- [x] T004 [P] Create vetorizer_lib/web/routes/__init__.py package marker
- [x] T005 [P] Create vetorizer_lib/web/services/__init__.py package marker
- [x] T006 [P] Create vetorizer_lib/web/models/__init__.py package marker
- [x] T007 Create vetorizer_lib/web/config.py with WebSettings class
- [x] T008 Create vetorizer_lib/web/app.py with FastAPI app skeleton and static/template mounting
- [x] T009 Create vetorizer_lib/web/cli.py with serve command using click or argparse
- [x] T010 Add CLI entry point to pyproject.toml [project.scripts] for `vetorizer` command
- [x] T011 [P] Create tests/unit/web/__init__.py and tests/integration/web/__init__.py
- [x] T012 [P] Create vetorizer_lib/web/templates/ and vetorizer_lib/web/static/ directories

**Checkpoint**: `python -m vetorizer_lib.web.cli serve` starts the web server

---

## Phase 2: Foundational

**Goal**: Shared infrastructure required by all user stories

### Models and Database

- [x] T013 Create vetorizer_lib/web/models/schemas.py with Pydantic schemas (DatabaseStatus, UploadStatus, QueryType enums; VectorDatabase, UploadJob, SearchResult, ErrorResponse models)
- [x] T014 Create vetorizer_lib/web/models/database.py with SQLite database initialization and connection management
- [x] T015 Create vetorizer_lib/web/deps.py with dependency injection (get_db, get_vetorizer_client)

### Base Templates (Jinja2 + HTMX)

- [x] T016 [P] Create vetorizer_lib/web/templates/base.html with HTML5 structure, TailwindCSS CDN, HTMX script
- [x] T017 [P] Create vetorizer_lib/web/templates/partials/nav.html with navigation links (Home, Search, Compare, Manage)
- [x] T018 [P] Create vetorizer_lib/web/templates/partials/toast.html for notification messages
- [x] T019 [P] Download htmx.min.js to vetorizer_lib/web/static/js/htmx.min.js
- [x] T020 Create vetorizer_lib/web/static/css/styles.css with TailwindCSS utility classes (or use CDN)

**Checkpoint**: Base template renders with navigation, HTMX loads correctly

---

## Phase 3: User Story 1 - Upload CSV and Create Named Vector Database (Priority: P1) 🎯 MVP

**Goal**: Users can upload CSV files and create named vector databases

**Independent Test**: Upload sample CSV, name database "test-products", verify it appears in database list with correct document count

### Backend Implementation for US1

- [x] T021 [US1] Create vetorizer_lib/web/services/database_service.py with create_database, get_database, list_databases functions
- [x] T022 [US1] Create vetorizer_lib/web/services/upload_service.py with process_csv, create_upload_job, update_job_progress functions
- [x] T023 [US1] Create vetorizer_lib/web/routes/upload.py with POST /api/upload endpoint (multipart file upload)
- [x] T024 [US1] Add POST /api/columns endpoint to vetorizer_lib/web/routes/upload.py for CSV column preview
- [x] T025 [US1] Add GET /api/upload/{jobId} endpoint for job status
- [x] T026 [US1] Add GET /api/upload/{jobId}/progress endpoint with SSE streaming
- [x] T027 [US1] Create vetorizer_lib/web/routes/databases.py with GET /api/databases endpoint (list all)
- [x] T028 [US1] Add POST /api/databases endpoint to create empty database
- [x] T029 [US1] Register upload and databases routers in vetorizer_lib/web/app.py

### Templates for US1

- [x] T030 [P] [US1] Create vetorizer_lib/web/templates/index.html with upload form and database list
- [x] T031 [P] [US1] Create vetorizer_lib/web/templates/partials/upload_form.html with file input, column selector, database name
- [x] T032 [P] [US1] Create vetorizer_lib/web/templates/partials/upload_progress.html with progress bar (HTMX SSE)
- [x] T033 [P] [US1] Create vetorizer_lib/web/templates/partials/database_list.html with database cards
- [x] T034 [US1] Add page route GET / to vetorizer_lib/web/app.py rendering index.html

**Checkpoint**: User Story 1 complete - CSV upload and database creation works end-to-end

---

## Phase 4: User Story 2 - Search Vector Database by Text (Priority: P2)

**Goal**: Users can search databases using natural language text queries

**Independent Test**: Select existing database, search for "comfortable running shoes", verify ranked results are returned

### Backend Implementation for US2

- [x] T035 [US2] Create vetorizer_lib/web/services/search_service.py with search_text function using vetorizer_lib
- [x] T036 [US2] Create vetorizer_lib/web/routes/search.py with POST /api/search endpoint
- [x] T037 [US2] Register search router in vetorizer_lib/web/app.py

### Templates for US2

- [x] T038 [P] [US2] Create vetorizer_lib/web/templates/search.html with search form and results area
- [x] T039 [P] [US2] Create vetorizer_lib/web/templates/partials/search_form.html with database selector and query input
- [x] T040 [P] [US2] Create vetorizer_lib/web/templates/partials/search_results.html with result cards (HTMX swap)
- [x] T041 [US2] Add page route GET /search to vetorizer_lib/web/app.py rendering search.html

**Checkpoint**: User Story 2 complete - Text search works independently

---

## Phase 5: User Story 3 - Search by Image (Priority: P3)

**Goal**: Users can search databases using image uploads

**Independent Test**: Upload image of red dress, verify fashion-related results are returned

### Backend Implementation for US3

- [x] T042 [US3] Add search_image function to vetorizer_lib/web/services/search_service.py using vetorizer_lib ImageEmbedder
- [x] T043 [US3] Add POST /api/search/image endpoint to vetorizer_lib/web/routes/search.py (multipart image upload)

### Templates for US3

- [x] T044 [P] [US3] Create vetorizer_lib/web/templates/partials/image_upload.html with drag-drop image upload
- [x] T045 [US3] Add image search tab to vetorizer_lib/web/templates/search.html

**Checkpoint**: User Story 3 complete - Image search works independently

---

## Phase 6: User Story 4 - Compare Search Results Across Databases (Priority: P4)

**Goal**: Users can compare search results from multiple databases side-by-side

**Independent Test**: Select 2 databases, search same query, verify side-by-side results display

### Backend Implementation for US4

- [x] T046 [US4] Update search_text in vetorizer_lib/web/services/search_service.py to support multiple database_ids
- [x] T047 [US4] Update POST /api/search endpoint to return results grouped by database

### Templates for US4

- [x] T048 [P] [US4] Create vetorizer_lib/web/templates/compare.html with multi-select and comparison layout
- [x] T049 [P] [US4] Create vetorizer_lib/web/templates/partials/comparison_results.html with side-by-side columns
- [x] T050 [US4] Add page route GET /compare to vetorizer_lib/web/app.py rendering compare.html

**Checkpoint**: User Story 4 complete - Comparison view works independently

---

## Phase 7: User Story 5 - Manage Vector Databases (Priority: P5)

**Goal**: Users can view, rename, and delete vector databases

**Independent Test**: View database list, rename a database, verify new name persists; delete a database, verify removal

### Backend Implementation for US5

- [x] T051 [US5] Add GET /api/databases/{databaseId} endpoint to vetorizer_lib/web/routes/databases.py
- [x] T052 [US5] Add PATCH /api/databases/{databaseId} endpoint (rename)
- [x] T053 [US5] Add DELETE /api/databases/{databaseId} endpoint
- [x] T054 [US5] Add update_database, delete_database functions to vetorizer_lib/web/services/database_service.py

### Templates for US5

- [x] T055 [P] [US5] Create vetorizer_lib/web/templates/manage.html with database management interface
- [x] T056 [P] [US5] Create vetorizer_lib/web/templates/partials/database_card.html with rename/delete actions
- [x] T057 [P] [US5] Create vetorizer_lib/web/templates/partials/confirm_dialog.html for delete confirmation
- [x] T058 [US5] Add page route GET /manage to vetorizer_lib/web/app.py rendering manage.html

**Checkpoint**: User Story 5 complete - Database management works independently

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Documentation, error handling, and quality improvements

- [x] T059 [P] Update README.md with web UI usage instructions and CLI command
- [x] T060 Add comprehensive error handling to all routes in vetorizer_lib/web/routes/
- [x] T061 Add loading states to all templates using HTMX indicators
- [x] T062 Add form validation to upload and search forms
- [x] T063 Run ruff linting and fix issues in vetorizer_lib/web/
- [x] T064 Verify all acceptance scenarios from spec.md pass manually

---

## Phase 9: Refactor - Remove SQLite, Add Configuration

**Goal**: Remove SQLite dependency, use Qdrant for metadata, add CLI configuration flags, add read-only config display in UI

### Backend Refactor

- [x] T065 Create vetorizer_lib/web/models/metadata_store.py with Qdrant-based metadata storage (collection `_vetorizer_metadata`)
- [x] T066 Remove aiosqlite from pyproject.toml dependencies
- [x] T067 Delete vetorizer_lib/web/models/database.py (SQLite schema)
- [x] T068 Refactor vetorizer_lib/web/services/database_service.py to use MetadataStore instead of SQLite
- [x] T069 Refactor vetorizer_lib/web/services/upload_service.py to use MetadataStore instead of SQLite
- [x] T070 Refactor vetorizer_lib/web/deps.py to provide MetadataStore instead of aiosqlite connection
- [x] T071 Update all routes (databases.py, upload.py, search.py) to use MetadataStore

### CLI Configuration

- [x] T072 Add CLI flags to vetorizer_lib/web/cli.py: --qdrant-path, --embedding-model, --max-upload-size
- [x] T073 Update vetorizer_lib/web/config.py to accept CLI overrides (via environment variables)

### UI Configuration Display

- [x] T074 Create GET /api/config endpoint in vetorizer_lib/web/routes/config.py (read-only)
- [x] T075 Create vetorizer_lib/web/templates/partials/config_display.html for read-only config view
- [x] T076 Add config display section to vetorizer_lib/web/templates/manage.html

### Embedding Model Selection

- [x] T077 Add embedding model dropdown to upload form (vetorizer_lib/web/templates/partials/upload_form.html)
- [x] T078 Update POST /api/upload to accept embedding_model parameter
- [x] T079 Store embedding_model per database in metadata

**Checkpoint**: Phase 9 complete - No SQLite dependency, configuration via CLI/env, read-only config in UI

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──────────────────────────────────────┐
                                                       │
Phase 2 (Foundational) ───────────────────────────────┤
                                                       │
Phase 3 (US1: Upload/Create) ─────────────────────────┤──► MVP Complete
                                                       │
Phase 4 (US2: Text Search) ───────────────────────────┤
         │                                             │
         ├─► Phase 5 (US3: Image Search)              │
         │                                             │
         └─► Phase 6 (US4: Compare) ──────────────────┤
                                                       │
Phase 7 (US5: Manage) ────────────────────────────────┤
                                                       │
Phase 8 (Polish) ─────────────────────────────────────┤
                                                       │
Phase 9 (Refactor: No SQLite, Config) ─────────────────┘
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 | Setup, Foundational | Phase 2 complete |
| US2 | US1 (needs databases to search) | Phase 3 complete |
| US3 | US2 (extends search) | Phase 4 complete |
| US4 | US2 (needs search working) | Phase 4 complete |
| US5 | US1 (needs databases to manage) | Phase 3 complete |

---

## Task Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | T001-T012 | Setup |
| 2 | T013-T020 | Foundational |
| 3 | T021-T034 | US1: Upload/Create |
| 4 | T035-T041 | US2: Text Search |
| 5 | T042-T045 | US3: Image Search |
| 6 | T046-T050 | US4: Compare |
| 7 | T051-T058 | US5: Manage |
| 8 | T059-T064 | Polish |
| 9 | T065-T079 | Refactor: No SQLite, Config |

**Total**: 79 tasks

---

## Implementation Strategy

### MVP Scope (Recommended First Delivery)

**Phases 1-3 only** (Tasks T001-T034):
- Project setup
- Foundational components  
- CSV upload and database creation
- Database listing

This delivers a working product where users can:
1. Launch web UI via CLI (`python -m vetorizer_lib.web.cli serve`)
2. Upload CSV files
3. Create named vector databases
4. View their databases

### Incremental Delivery

| Delivery | Phases | New Capability |
|----------|--------|----------------|
| MVP | 1-3 | Upload CSV, create databases |
| v0.2 | +4 | Text search |
| v0.3 | +5 | Image search |
| v0.4 | +6 | Compare results |
| v0.5 | +7 | Database management |
| v1.0 | +8 | Production-ready |

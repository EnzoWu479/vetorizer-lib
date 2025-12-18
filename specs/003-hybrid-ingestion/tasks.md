# Tasks: Ingestão Híbrida (Texto/Imagem)

**Input**: Design documents from `/specs/003-hybrid-ingestion/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: MANDATORY - TDD approach required per constitution (Principle II)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US0, US1, US2, US3)
- All paths include exact file locations

## Path Conventions

- **Library root**: `vetorizer_lib/`
- **Web module**: `vetorizer_lib/web/`
- **Tests**: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [X] T001 Add python-magic-bin dependency to pyproject.toml for MIME validation
- [X] T002 [P] Install and verify sentence-transformers all-MiniLM-L6-v2 model (384d text embedder)
- [X] T003 [P] Install and verify openai/clip-vit-base-patch16 model (512d image embedder, upgrade from patch32)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Extend IngestMode enum in vetorizer_lib/models/hybrid.py to support TEXT, IMAGE, HYBRID modes
- [X] T005 [P] Implement per-modality vector normalization function in vetorizer_lib/models/hybrid.py (critical fix for 80/20 imbalance)
- [X] T006 [P] Create ValidationResult and BatchValidationSummary models in vetorizer_lib/web/models/schemas.py
- [X] T007 Create CreateDatabaseRequest schema with mode, embedder config, files in vetorizer_lib/web/models/schemas.py
- [X] T008 Create IngestionResult schema with statistics in vetorizer_lib/web/models/schemas.py
- [X] T009 [P] Implement MIME type validation service in vetorizer_lib/web/services/validation_service.py
- [X] T010 Setup embedder singleton manager in vetorizer_lib/embedders/manager.py for lazy loading with FP16 support

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 0 - Criar Banco de Dados via UI com Upload (Priority: P0) 🎯 MVP

**Goal**: Enable users to create database on home page with mode selection (text/image/hybrid) and document upload in single operation

**Independent Test**: Access home page, click "Create Database", select mode, upload files, verify database created with documents ingested

### Tests for User Story 0 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US0] Unit test for database creation validation logic in tests/unit/web/test_database_validation.py
- [X] T012 [P] [US0] Unit test for file validation service in tests/unit/web/test_file_validation.py
- [X] T013 [P] [US0] Contract test for POST /api/databases endpoint in tests/contract/test_api.py
- [X] T014 [P] [US0] Contract test for POST /api/databases/validate endpoint in tests/contract/test_api.py
- [X] T015 [US0] Integration test for complete database creation workflow in tests/integration/web/test_create_database_workflow.py

### Implementation for User Story 0

#### Backend Models & Schemas

- [X] T016 [P] [US0] Extend DatabaseMetadata model with ingest_mode, embedder configs, hybrid metadata in vetorizer_lib/web/models/database.py
- [X] T017 [P] [US0] Add FileValidationResult schema with filename, status, errors, warnings in vetorizer_lib/web/models/schemas.py

#### Backend Services

- [X] T018 [US0] Implement batch file validation in vetorizer_lib/web/services/validation_service.py (parallel validation, max 5 concurrent)
- [X] T019 [US0] Extend DatabaseService.create_database() to support hybrid mode with embedder config in vetorizer_lib/web/services/database_service.py
- [X] T020 [US0] Implement transactional database creation + ingestion in vetorizer_lib/web/services/database_service.py
- [X] T021 [US0] Add rollback logic for failed ingestion in vetorizer_lib/web/services/database_service.py

#### Backend Routes

- [X] T022 [US0] Create POST /api/databases endpoint with multipart support in vetorizer_lib/web/routes/databases.py
- [X] T023 [US0] Create POST /api/databases/validate endpoint for pre-validation in vetorizer_lib/web/routes/databases.py
- [X] T024 [US0] Add validation summary response formatting in vetorizer_lib/web/routes/databases.py

#### Frontend UI Components

- [X] T025 [P] [US0] Create create_database_modal.html partial with modal structure in vetorizer_lib/web/templates/partials/
- [X] T026 [P] [US0] Add radio button mode selection (Text/Image/Hybrid) to create_database_modal.html
- [X] T027 [P] [US0] Add collapsible advanced section with embedder config in create_database_modal.html
- [X] T028 [P] [US0] Add file upload area with drag-and-drop in create_database_modal.html
- [X] T029 [US0] Add validation summary display component to create_database_modal.html (shows X processed, Y ignored, Z failed)
- [X] T030 [US0] Add per-file validation details expandable accordion in create_database_modal.html
- [X] T031 [US0] Add final result statistics display in create_database_modal.html

#### Frontend Integration

- [X] T032 [US0] Add "Create New Database" button to vetorizer_lib/web/templates/index.html home page
- [X] T033 [US0] Wire modal open/close with HTMX in vetorizer_lib/web/templates/index.html
- [X] T034 [US0] Add modal styling to vetorizer_lib/web/static/css/styles.css (overlay, focus trap, ARIA)
- [X] T035 [US0] Implement form submission with progress indicator using HTMX in create_database_modal.html
- [X] T036 [US0] Add client-side validation and error display in create_database_modal.html
- [X] T037 [US0] Add success toast notification after database creation in vetorizer_lib/web/templates/partials/toast.html

**Checkpoint**: User Story 0 complete - users can create hybrid databases via UI with full validation and feedback

---

## Phase 4: User Story 1 - Ingerir Dataset com Modo Híbrido (Priority: P1)

**Goal**: Enable dataset ingestion with mode selection (text/image/hybrid) and generate appropriate vector representation

**Independent Test**: Ingest dataset with text-only, image-only, and hybrid documents, verify all accepted and available for search

### Tests for User Story 1 ⚠️

- [ ] T038 [P] [US1] Unit test for text-only ingestion in tests/unit/test_ingest_text.py
- [ ] T039 [P] [US1] Unit test for image-only ingestion in tests/unit/test_ingest_image.py
- [ ] T040 [P] [US1] Unit test for hybrid ingestion in tests/unit/test_ingest_hybrid.py
- [ ] T041 [P] [US1] Contract test for POST /api/upload with text mode in tests/contract/test_api.py
- [ ] T042 [P] [US1] Contract test for POST /api/upload with image mode in tests/contract/test_api.py
- [ ] T043 [P] [US1] Contract test for POST /api/upload with hybrid mode in tests/contract/test_api.py
- [ ] T044 [US1] Integration test for mixed dataset ingestion in tests/integration/test_hybrid_upload.py

### Implementation for User Story 1

- [ ] T045 [P] [US1] Extend TextEmbedder to support normalization in vetorizer_lib/embedders/text.py
- [ ] T046 [P] [US1] Extend ImageEmbedder to support custom CLIP models in vetorizer_lib/embedders/image.py
- [ ] T047 [US1] Implement hybrid vector generation with proper concatenation in vetorizer_lib/models/hybrid.py
- [ ] T048 [US1] Extend CSVIngestor to support mode parameter in vetorizer_lib/ingest/csv.py
- [ ] T049 [US1] Add conditional embedder selection logic in vetorizer_lib/ingest/csv.py
- [ ] T050 [US1] Implement metadata recording (modalities, dimensions) in vetorizer_lib/ingest/csv.py
- [ ] T051 [US1] Add document filtering for missing modalities in vetorizer_lib/ingest/csv.py
- [ ] T052 [US1] Extend QdrantStore to support hybrid vector metadata in vetorizer_lib/stores/qdrant.py
- [ ] T053 [US1] Update POST /api/upload route to handle hybrid mode in vetorizer_lib/web/routes/upload.py

**Checkpoint**: User Story 1 complete - dataset ingestion works for all three modes with proper validation

---

## Phase 5: User Story 2 - Buscar com Consulta Multimodal (Priority: P2)

**Goal**: Enable search using text, image, or hybrid queries to find relevant documents

**Independent Test**: Execute searches with text/image/hybrid queries, verify results returned for compatible documents

### Tests for User Story 2 ⚠️

- [ ] T054 [P] [US2] Unit test for text query vector generation in tests/unit/test_search_text.py
- [ ] T055 [P] [US2] Unit test for image query vector generation in tests/unit/test_search_image.py
- [ ] T056 [P] [US2] Unit test for hybrid query vector generation in tests/unit/test_search_hybrid.py
- [ ] T057 [P] [US2] Contract test for POST /api/search with text query in tests/contract/test_api.py
- [ ] T058 [P] [US2] Contract test for POST /api/search/image in tests/contract/test_api.py
- [ ] T059 [P] [US2] Contract test for POST /api/search/hybrid in tests/contract/test_api.py
- [ ] T060 [US2] Integration test for multimodal search workflow in tests/integration/test_search_multimodal.py

### Implementation for User Story 2

- [ ] T061 [P] [US2] Create SearchQuery model with query_type field in vetorizer_lib/web/models/schemas.py
- [ ] T062 [US2] Implement query vector generation service in vetorizer_lib/web/services/search_service.py
- [ ] T063 [US2] Add mode compatibility validation in vetorizer_lib/web/services/search_service.py
- [ ] T064 [US2] Extend QdrantStore.search() to support hybrid queries in vetorizer_lib/stores/qdrant.py
- [ ] T065 [US2] Create POST /api/search/hybrid endpoint in vetorizer_lib/web/routes/search.py
- [ ] T066 [US2] Add hybrid search form to vetorizer_lib/web/templates/partials/hybrid_search.html
- [ ] T067 [US2] Wire hybrid search UI in vetorizer_lib/web/templates/search.html
- [ ] T068 [US2] Add results formatting for hybrid search in vetorizer_lib/web/templates/partials/search_results.html

**Checkpoint**: User Story 2 complete - all search modes functional with proper compatibility checks

---

## Phase 6: User Story 3 - Rastreabilidade do Vetor Híbrido (Priority: P3)

**Goal**: Ensure hybrid vector composition is deterministic and traceable for consistency

**Independent Test**: Ingest same dataset twice with same config, verify vector format and metadata consistent

### Tests for User Story 3 ⚠️

- [ ] T069 [P] [US3] Unit test for deterministic concatenation in tests/unit/test_hybrid_vector.py
- [ ] T070 [P] [US3] Unit test for metadata recording in tests/unit/test_hybrid_metadata.py
- [ ] T071 [US3] Integration test for repeated ingestion consistency in tests/integration/test_hybrid_consistency.py

### Implementation for User Story 3

- [ ] T072 [P] [US3] Add HybridVectorMetadata model with modalities, order, dimensions in vetorizer_lib/models/hybrid.py
- [ ] T073 [US3] Implement metadata serialization/deserialization in vetorizer_lib/models/hybrid.py
- [ ] T074 [US3] Record concatenation order in metadata during ingestion in vetorizer_lib/ingest/csv.py
- [ ] T075 [US3] Add schema_version field to metadata in vetorizer_lib/models/hybrid.py
- [ ] T076 [US3] Implement metadata retrieval endpoint GET /api/databases/{id}/metadata in vetorizer_lib/web/routes/databases.py
- [ ] T077 [US3] Add metadata display to database details UI in vetorizer_lib/web/templates/manage.html

**Checkpoint**: User Story 3 complete - hybrid vectors fully traceable with deterministic generation

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories and final validation

- [ ] T078 [P] Update README.md with hybrid ingestion examples and mode selection guide
- [ ] T079 [P] Add comprehensive docstrings to all new functions (Google style)
- [ ] T080 [P] Update vetorizer_lib/web/models/schemas.py with OpenAPI schema annotations
- [ ] T081 [P] Add logging for all hybrid operations with structured context
- [ ] T082 Add error handling middleware for validation errors in vetorizer_lib/web/app.py
- [ ] T083 Add rate limiting for upload endpoints in vetorizer_lib/web/app.py
- [ ] T084 Implement file cleanup for failed uploads in vetorizer_lib/web/services/upload_service.py
- [ ] T085 Add performance monitoring for embedder operations in vetorizer_lib/embedders/manager.py
- [ ] T086 Run ruff linting on all modified files and fix issues
- [ ] T087 Run mypy type checking in strict mode and resolve all errors
- [ ] T088 Verify pytest coverage >90% for new code with pytest-cov
- [ ] T089 Execute quickstart.md validation with test dataset
- [ ] T090 Security audit: sanitize file paths, validate database names, check quota enforcement

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 0 (Phase 3)**: Depends on Foundational completion - MVP target
- **User Story 1 (Phase 4)**: Depends on Foundational completion - Can run parallel to US0
- **User Story 2 (Phase 5)**: Depends on US1 completion (needs ingested data to search)
- **User Story 3 (Phase 6)**: Depends on US1 completion (needs ingestion to track)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 0 (P0)**: Depends on Foundational - Enables UI database creation (MVP entry point)
- **User Story 1 (P1)**: Depends on Foundational - Independent of US0 (can run parallel)
- **User Story 2 (P2)**: Depends on US1 - Needs documents ingested to search
- **User Story 3 (P3)**: Depends on US1 - Needs ingestion logic to add traceability

### Critical Path

**Foundational → US0 (UI) + US1 (Ingestion) → US2 (Search) → US3 (Metadata)**

### Parallel Opportunities

**Phase 1 (Setup)**: T002 and T003 can run in parallel (model downloads)

**Phase 2 (Foundational)**: 
- T005, T006, T009, T010 can run in parallel (different files)

**Phase 3 (US0)**:
- Tests: T011, T012, T013, T014 can run in parallel
- Models: T016, T017 can run in parallel
- UI Components: T025, T026, T027, T028 can run in parallel

**Phase 4 (US1)**:
- Tests: T038-T043 can run in parallel
- Embedders: T045, T046 can run in parallel

**Phase 5 (US2)**:
- Tests: T054-T059 can run in parallel
- T061 can run parallel with other tasks

**Phase 6 (US3)**:
- Tests: T069, T070 can run in parallel
- T072, T073 can run in parallel

**Phase 7 (Polish)**:
- T078, T079, T080, T081 can all run in parallel (documentation)

---

## Parallel Example: User Story 0 (UI Database Creation)

```bash
# Launch all tests together (Phase 3, Tests section):
T011: Unit test for database validation
T012: Unit test for file validation  
T013: Contract test for POST /api/databases
T014: Contract test for POST /api/databases/validate

# Wait for test scaffolds, then launch backend models:
T016: Extend DatabaseMetadata model
T017: Add FileValidationResult schema

# Launch UI components in parallel:
T025: Create modal structure
T026: Add radio buttons
T027: Add advanced section
T028: Add file upload area

# Complete remaining tasks sequentially
```

---

## Implementation Strategy

### MVP First (User Story 0 Only)

**Target**: Complete database creation via UI with validation and upload

1. Complete Phase 1: Setup (install dependencies, verify models)
2. Complete Phase 2: Foundational (core models, schemas, services) ⚠️ BLOCKS EVERYTHING
3. Complete Phase 3: User Story 0 (UI-driven database creation)
4. **STOP and VALIDATE**: Test database creation workflow end-to-end
5. Deploy/demo UI functionality

**Estimated MVP Tasks**: ~37 tasks (T001-T037)

### Incremental Delivery

1. **Foundation** (Setup + Foundational) → Infrastructure ready
2. **MVP** (+ User Story 0) → UI database creation ✅ Independently testable
3. **Core Ingestion** (+ User Story 1) → Hybrid ingestion backend ✅ Independently testable
4. **Search** (+ User Story 2) → Multimodal search ✅ Independently testable
5. **Traceability** (+ User Story 3) → Metadata tracking ✅ Independently testable
6. **Production Ready** (+ Polish) → Full feature complete

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers (after Foundational phase completes):

- **Developer A**: User Story 0 (UI/Frontend focus)
- **Developer B**: User Story 1 (Ingestion backend)
- **Developer C**: User Story 2 (Search) - starts after US1 core complete

Stories integrate naturally through shared models from Foundational phase.

---

## Notes

- **[P] tasks**: Different files, no dependencies - safe to parallelize
- **[Story] labels**: Map tasks to user stories for traceability
- **TDD Mandatory**: All test tasks MUST be written first and FAIL before implementation
- **Independent Stories**: Each user story is fully functional and testable on its own
- **Checkpoint Validation**: Stop at each checkpoint to verify story independently
- **Commit Strategy**: Commit after each task or logical group of [P] tasks
- **Critical Fix**: Per-modality normalization (T005) addresses 80/20 imbalance issue
- **Model Upgrade**: CLIP patch16 (T003) provides +4.8% accuracy improvement
- **File Paths**: All paths are absolute from repository root
- **Coverage Target**: >90% for new code (enforced in T088)

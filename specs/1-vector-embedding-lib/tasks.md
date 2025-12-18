# Tasks: Vector Embedding Library

**Input**: Design documents from `/specs/1-vector-embedding-lib/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are included per Constitution Principle II (TDD required).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Source**: `vetorizer_lib/` at repository root
- **Tests**: `tests/` with unit/integration/contract subdirectories

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize uv project and basic structure

- [x] T001 Initialize uv project with `uv init` and configure pyproject.toml per research.md
- [x] T002 [P] Create package directory structure: vetorizer_lib/ with __init__.py
- [x] T003 [P] Create tests directory structure: tests/unit/, tests/integration/, tests/contract/
- [x] T004 [P] Create vetorizer_lib/exceptions.py with VetorizerError hierarchy
- [x] T005 [P] Create tests/conftest.py with shared pytest fixtures
- [x] T006 [P] Create README.md with project description and installation instructions
- [x] T007 [P] Create CHANGELOG.md with initial version entry
- [x] T008 Run `uv sync --dev` to install dependencies and generate uv.lock

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core abstractions that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create vetorizer_lib/models/__init__.py with module exports
- [x] T010 [P] Create enums (ContentType, Modality, DistanceMetric) in vetorizer_lib/models/config.py
- [x] T011 [P] Create Document dataclass in vetorizer_lib/models/document.py
- [x] T012 [P] Create SearchResult dataclass in vetorizer_lib/models/document.py
- [x] T013 [P] Create IngestResult dataclass in vetorizer_lib/models/document.py
- [x] T014 [P] Create VectorStoreConfig dataclass in vetorizer_lib/models/config.py
- [x] T015 [P] Create IngestConfig dataclass in vetorizer_lib/models/config.py
- [x] T016 Create Embedder protocol in vetorizer_lib/embedders/base.py
- [x] T017 [P] Create VectorStore protocol in vetorizer_lib/stores/base.py
- [x] T018 [P] Create vetorizer_lib/embedders/__init__.py with module exports
- [x] T019 [P] Create vetorizer_lib/stores/__init__.py with module exports
- [x] T020 [P] Create vetorizer_lib/ingest/__init__.py with module exports
- [x] T021 Create tests/unit/test_models.py with tests for all dataclasses and enums

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Ingest CSV Data (Priority: P1) 🎯 MVP

**Goal**: Ingest data from CSV files into vector database with batch processing

**Independent Test**: Provide sample CSV, run ingest, verify records in Qdrant with embeddings

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T022 [P] [US1] Create tests/unit/test_ingest.py with CSV parsing tests (mock embedder/store)
- [x] T023 [P] [US1] Create tests/unit/test_embedders.py with TextEmbedder tests (mock model)
- [x] T024 [P] [US1] Create tests/integration/test_qdrant.py with QdrantStore upsert tests
- [x] T025 [P] [US1] Create tests/contract/test_api.py with ingest_csv contract tests

### Implementation for User Story 1

- [x] T026 [US1] Implement TextEmbedder in vetorizer_lib/embedders/text.py using sentence-transformers
- [x] T027 [US1] Implement QdrantStore in vetorizer_lib/stores/qdrant.py with upsert method
- [x] T028 [US1] Implement CSV reader with chunked processing in vetorizer_lib/ingest/csv.py
- [x] T029 [US1] Implement VetorizerClient.__init__ in vetorizer_lib/client.py
- [x] T030 [US1] Implement VetorizerClient.ingest_csv in vetorizer_lib/client.py
- [x] T031 [US1] Add progress callback support to ingest_csv
- [x] T032 [US1] Add error handling for missing files, invalid columns, empty rows
- [x] T033 [US1] Export public API in vetorizer_lib/__init__.py (VetorizerClient, IngestResult)

**Checkpoint**: User Story 1 complete - CSV ingestion works independently

---

## Phase 4: User Story 2 - Search Vector Database (Priority: P2)

**Goal**: Search database using natural language queries with similarity scoring

**Independent Test**: Query populated database, verify results ranked by similarity

### Tests for User Story 2

- [x] T034 [P] [US2] Add search tests to tests/unit/test_embedders.py (query embedding)
- [x] T035 [P] [US2] Add search tests to tests/integration/test_qdrant.py (QdrantStore.search)
- [x] T036 [P] [US2] Add search contract tests to tests/contract/test_api.py

### Implementation for User Story 2

- [x] T037 [US2] Implement QdrantStore.search method in vetorizer_lib/stores/qdrant.py
- [x] T038 [US2] Implement VetorizerClient.search in vetorizer_lib/client.py
- [x] T039 [US2] Add limit parameter support to search
- [x] T040 [US2] Add min_score threshold filtering to search
- [x] T041 [US2] Add metadata filter support to search
- [x] T042 [US2] Export SearchResult in vetorizer_lib/__init__.py

**Checkpoint**: User Stories 1 AND 2 work independently - core ingest+search complete

---

## Phase 5: User Story 3 - Configure Embedding Model (Priority: P3)

**Goal**: Allow users to choose HuggingFace models for embeddings

**Independent Test**: Initialize with different model names, verify embeddings use correct model

### Tests for User Story 3

- [x] T043 [P] [US3] Add model configuration tests to tests/unit/test_embedders.py
- [x] T044 [P] [US3] Add invalid model error tests to tests/unit/test_embedders.py

### Implementation for User Story 3

- [x] T045 [US3] Add model_name parameter validation to TextEmbedder in vetorizer_lib/embedders/text.py
- [x] T046 [US3] Implement model loading with error handling (ModelLoadError) in vetorizer_lib/embedders/text.py
- [x] T047 [US3] Add embedding dimension detection to TextEmbedder
- [x] T048 [US3] Update VetorizerClient to pass model_name to embedder
- [x] T049 [US3] Add model info logging on initialization

**Checkpoint**: User Stories 1, 2, AND 3 work - text embedding fully configurable

---

## Phase 6: User Story 4 - Image Embedding Support (Priority: P4)

**Goal**: Embed images using CLIP for multimodal search

**Independent Test**: Ingest images, search with text or image query, verify cross-modal results

### Tests for User Story 4

- [x] T050 [P] [US4] Create tests/unit/test_image_embedder.py with ImageEmbedder tests
- [x] T051 [P] [US4] Add image ingest tests to tests/integration/test_client.py
- [x] T052 [P] [US4] Add image search contract tests to tests/contract/test_api.py

### Implementation for User Story 4

- [x] T053 [US4] Implement ImageEmbedder in vetorizer_lib/embedders/image.py using CLIP
- [x] T054 [US4] Add image loading and preprocessing to ImageEmbedder
- [x] T055 [US4] Implement VetorizerClient.ingest_images in vetorizer_lib/client.py
- [x] T056 [US4] Implement VetorizerClient.search_by_image in vetorizer_lib/client.py
- [x] T057 [US4] Add modality detection to VetorizerClient (text vs image model)
- [x] T058 [US4] Export ingest_images, search_by_image in vetorizer_lib/__init__.py

**Checkpoint**: All user stories complete - full text and image embedding support

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and quality improvements

- [x] T059 [P] Update README.md with complete usage examples from quickstart.md
- [x] T060 [P] Add Google-style docstrings to all public functions per Constitution V
- [x] T061 [P] Run mypy type checking and fix any type errors
- [x] T062 [P] Run ruff linting and fix any style issues
- [x] T063 [P] Update CHANGELOG.md with v0.1.0 release notes
- [x] T064 Create tests/integration/test_client.py with full end-to-end tests
- [x] T065 Add performance test for 10K row ingestion (<5 min requirement)
- [x] T066 Verify all tests pass with `uv run pytest`
- [x] T067 Run quickstart.md validation - ensure all examples work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Phase 2
  - US2 (P2): Can start after Phase 2 (uses US1 data for testing but independent)
  - US3 (P3): Can start after Phase 2 (enhances US1/US2 but independent)
  - US4 (P4): Can start after Phase 2 (separate embedder, independent)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|------------|---------------------|
| US1 (Ingest) | Phase 2 only | US2, US3, US4 |
| US2 (Search) | Phase 2 only | US1, US3, US4 |
| US3 (Model Config) | Phase 2 only | US1, US2, US4 |
| US4 (Images) | Phase 2 only | US1, US2, US3 |

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Models/dataclasses before services
3. Services before client methods
4. Core implementation before error handling
5. Story complete before moving to next priority

---

## Parallel Execution Examples

### Phase 1 Parallel Tasks

```bash
# All [P] tasks in Phase 1 can run together:
T002: Create package directory structure
T003: Create tests directory structure
T004: Create exceptions.py
T005: Create conftest.py
T006: Create README.md
T007: Create CHANGELOG.md
```

### Phase 2 Parallel Tasks

```bash
# After T009 completes, these can run in parallel:
T010: Create enums
T011: Create Document
T012: Create SearchResult
T013: Create IngestResult
T014: Create VectorStoreConfig
T015: Create IngestConfig
```

### User Story 1 Parallel Tests

```bash
# All US1 tests can be written in parallel:
T022: test_ingest.py
T023: test_embedders.py
T024: test_qdrant.py (integration)
T025: test_api.py (contract)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Ingest)
4. **STOP and VALIDATE**: Test CSV ingestion independently
5. Deploy/demo if ready - users can ingest data

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP: Can ingest CSV data**
3. Add User Story 2 → Test independently → **Can search data**
4. Add User Story 3 → Test independently → **Can configure models**
5. Add User Story 4 → Test independently → **Full multimodal support**

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Phase 2 is done:
   - Developer A: User Story 1 (Ingest)
   - Developer B: User Story 2 (Search)
   - Developer C: User Story 3 (Model Config)
   - Developer D: User Story 4 (Images)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution requires TDD - all tests written before implementation

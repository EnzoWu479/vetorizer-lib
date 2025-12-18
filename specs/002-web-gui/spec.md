# Feature Specification: Web GUI for Vector Database Management

**Feature Branch**: `002-web-gui`  
**Created**: 2024-12-17  
**Status**: Draft  
**Input**: User description: "Interface gráfica web que possibilita upload de CSV para ingestão, nomear bases vetorizadas, buscas por imagem/texto/arquivo, e comparar resultados entre bases"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload CSV and Create Named Vector Database (Priority: P1)

As a user, I want to upload a CSV file through a web interface and create a named vector database so that I can organize and manage multiple datasets for semantic search.

The user accesses the web application, selects a CSV file from their computer, specifies which column contains the text to be embedded, gives the vector database a meaningful name, and initiates the ingestion process. The system shows progress during ingestion and confirms when the database is ready for searching.

**Why this priority**: This is the foundational feature - without the ability to create vector databases, no other functionality (search, comparison) is possible. It delivers immediate value by enabling data ingestion through a user-friendly interface.

**Independent Test**: Can be fully tested by uploading a sample CSV file, naming the database "test-products", and verifying the database appears in the list of available databases with the correct document count.

**Acceptance Scenarios**:

1. **Given** the web application is open, **When** I upload a valid CSV file, select the content column, enter "my-products" as the database name, and click "Create", **Then** the system ingests the data and displays a success message with the number of documents processed.
2. **Given** I have uploaded a CSV file, **When** I do not specify a database name, **Then** the system prevents submission and displays a validation error.
3. **Given** a database named "my-products" already exists, **When** I try to create another database with the same name, **Then** the system warns me and offers to overwrite or choose a different name.
4. **Given** I am uploading a large CSV file, **When** ingestion is in progress, **Then** the system displays a progress indicator showing the percentage complete.

---

### User Story 2 - Search Vector Database by Text (Priority: P2)

As a user, I want to search a vector database using natural language text queries so that I can find semantically similar content without needing exact keyword matches.

The user selects a previously created vector database from a dropdown, enters a text query in a search box, and submits the search. The system returns a ranked list of results showing the content, similarity score, and any metadata associated with each result.

**Why this priority**: Text search is the most common use case for vector databases and provides immediate utility once data is ingested. It builds directly on US1.

**Independent Test**: Can be tested by selecting an existing database, entering a search query like "comfortable running shoes", and verifying results are returned sorted by relevance score.

**Acceptance Scenarios**:

1. **Given** a vector database "products" exists with product descriptions, **When** I select it and search for "comfortable running shoes", **Then** the system returns relevant product descriptions ranked by similarity score.
2. **Given** I have performed a search, **When** viewing results, **Then** each result displays the content, similarity score (0-100%), and associated metadata.
3. **Given** no vector databases exist, **When** I try to search, **Then** the system displays a message indicating I need to create a database first.
4. **Given** I search for something with no similar content, **When** results are returned, **Then** the system shows an empty results message or low-confidence results with appropriate indication.

---

### User Story 3 - Search by Image (Priority: P3)

As a user, I want to search a vector database using an image so that I can find visually or semantically similar content across my data.

The user selects a vector database, uploads an image file (or provides an image URL), and submits the search. The system uses a multimodal embedding model to find content similar to the image and returns ranked results.

**Why this priority**: Image search extends the utility of the system to visual use cases, but requires the text search foundation to be in place first.

**Independent Test**: Can be tested by uploading a photo of a red dress and verifying the system returns fashion-related content from the database.

**Acceptance Scenarios**:

1. **Given** a vector database exists with fashion product descriptions, **When** I upload an image of a red dress and search, **Then** the system returns content semantically related to red dresses.
2. **Given** I want to search by image, **When** I upload a file, **Then** the system accepts common image formats (JPG, PNG, WebP).
3. **Given** I upload an invalid or corrupted image file, **When** I submit the search, **Then** the system displays an appropriate error message.

---

### User Story 4 - Compare Search Results Across Databases (Priority: P4)

As a user, I want to run the same search query against multiple vector databases and compare the results side-by-side so that I can evaluate which database or embedding model produces better results for my use case.

The user selects two or more databases, enters a search query (text or image), and submits. The system displays results from each database in parallel columns, allowing visual comparison of rankings and scores.

**Why this priority**: Comparison is an advanced feature that requires multiple databases and search functionality to already exist. It provides value for users evaluating different data sources or configurations.

**Independent Test**: Can be tested by creating two databases with different content, running the same query against both, and verifying results appear in side-by-side columns.

**Acceptance Scenarios**:

1. **Given** I have databases "products-v1" and "products-v2", **When** I select both and search for "wireless headphones", **Then** the system displays results from each database in separate columns.
2. **Given** I am comparing results, **When** viewing the comparison, **Then** I can see the similarity scores from each database to evaluate which produced better matches.
3. **Given** I want to compare more than two databases, **When** I select up to 4 databases, **Then** the system displays all results in a scrollable comparison view.
4. **Given** I select only one database for comparison, **When** I try to compare, **Then** the system prompts me to select at least two databases.

---

### User Story 5 - Manage Vector Databases (Priority: P5)

As a user, I want to view, rename, and delete my vector databases so that I can keep my workspace organized.

The user accesses a database management view that lists all created databases with their names, document counts, and creation dates. From this view, they can rename or delete databases.

**Why this priority**: Management features are important for long-term usability but not required for core functionality.

**Independent Test**: Can be tested by viewing the database list, renaming a database, and verifying the new name persists.

**Acceptance Scenarios**:

1. **Given** I have created multiple databases, **When** I access the management view, **Then** I see a list of all databases with name, document count, and creation date.
2. **Given** I want to rename a database, **When** I click rename and enter a new name, **Then** the database is renamed and the new name appears everywhere.
3. **Given** I want to delete a database, **When** I click delete and confirm, **Then** the database is permanently removed.
4. **Given** I try to delete a database, **When** the confirmation dialog appears, **Then** I must explicitly confirm to prevent accidental deletion.

---

### Edge Cases

- What happens when the CSV file is empty or contains only headers?
- What happens when the selected content column contains empty values?
- How does the system handle very large CSV files (>100MB)?
- What happens when the user's browser loses connection during ingestion?
- How does the system handle special characters or non-UTF8 encoding in CSV files?
- What happens when the user uploads a non-CSV file with a .csv extension?
- How does the system handle concurrent uploads from the same user?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a web interface accessible via modern browsers (Chrome, Firefox, Safari, Edge)
- **FR-002**: System MUST allow users to upload CSV files up to 100MB in size
- **FR-003**: System MUST allow users to select which column in the CSV contains the content to embed
- **FR-004**: System MUST allow users to assign a unique name to each vector database
- **FR-005**: System MUST display ingestion progress with percentage complete
- **FR-006**: System MUST persist vector databases between sessions
- **FR-007**: System MUST provide a text search interface with a query input field
- **FR-008**: System MUST display search results with content, similarity score, and metadata
- **FR-009**: System MUST allow users to select which database to search
- **FR-010**: System MUST support image upload for image-based search
- **FR-011**: System MUST support comparison of search results across 2-4 databases
- **FR-012**: System MUST provide a database management interface to list, rename, and delete databases
- **FR-013**: System MUST validate CSV files before processing and display clear error messages for invalid files
- **FR-014**: System MUST prevent duplicate database names
- **FR-015**: System MUST require confirmation before deleting a database
- **FR-016**: System MUST allow users to select an embedding model when creating a vector database, with a configurable default
- **FR-017**: System MUST provide an initial configuration mechanism via CLI and/or environment variables to set host, port, qdrant_path, max_upload_size, and default embedding model; the UI MUST display the effective configuration read-only

### Key Entities

- **VectorDatabase**: A named collection of embedded documents. Attributes: unique name, document count, creation timestamp, embedding model used.
- **SearchQuery**: A user's search request. Attributes: query type (text/image), query content, target database(s), result limit.
- **SearchResult**: A single result from a search. Attributes: content, similarity score, metadata, source database.
- **ComparisonView**: A side-by-side display of results from multiple databases for the same query.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload a CSV and create a named vector database in under 3 minutes for files up to 10,000 rows
- **SC-002**: Search results are returned in under 2 seconds for databases with up to 100,000 documents
- **SC-003**: Users can complete a text search workflow (select database, enter query, view results) in under 30 seconds
- **SC-004**: The comparison view displays results from up to 4 databases simultaneously without horizontal scrolling on standard desktop screens (1920px width)
- **SC-005**: 90% of users can successfully upload their first CSV and perform a search without consulting documentation
- **SC-006**: System handles 10 concurrent users without performance degradation

## Clarifications

### Session 2024-12-17

- Q: Should the frontend be a separate React/TypeScript application or integrated into the Python library? → A: Python-based, integrated into vetorizer_lib
- Q: How should users launch the web interface? → A: Via CLI command (e.g., `vetorizer serve` or `python -m vetorizer_lib serve`)

### Session 2025-12-17

- Q: Where should vector database metadata be stored (no SQLite)? → A: Qdrant (special collection `_vetorizer_metadata`)
- Q: How should users configure embedding model when creating a database? → A: UI dropdown per database, with a CLI-configurable default
- Q: What should be included in initial configuration via UI/CLI? → A: qdrant_path, default_embedding_model, max_upload_size, host, port
- Q: Should initial configuration be persisted via UI? → A: No; configure via CLI flags and/or environment variables
- Q: What should UI configuration provide? → A: Read-only display of effective configuration; global changes via CLI/env only

## Technical Constraints

- **TC-001**: The web interface MUST be implemented in Python (no separate JavaScript/TypeScript frontend)
- **TC-002**: The web interface MUST be part of the vetorizer_lib package, not a separate project
- **TC-003**: Users MUST be able to launch the web interface via a CLI command
- **TC-004**: The web interface SHOULD use a Python web framework that serves both backend API and frontend HTML/CSS/JS
- **TC-005**: The web interface MUST NOT require SQLite; metadata MUST be stored in Qdrant

## Assumptions

- Users have CSV files with a clear text column suitable for embedding
- Users have modern web browsers with JavaScript enabled
- The underlying vetorizer_lib library handles the actual embedding and vector storage
- File uploads are handled server-side (not client-side processing)
- Vector databases are stored locally on the server (not cloud-distributed)
- Users launch the web interface from the command line

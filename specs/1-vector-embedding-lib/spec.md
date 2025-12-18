# Feature Specification: Vector Embedding Library

**Feature Branch**: `1-vector-embedding-lib`  
**Created**: 2025-12-17  
**Status**: Draft  
**Input**: User description: "Build a Python lib using uv that you can choose a model from HuggingFace, choose a vectorized database to make embedding on a text/image and store on a vectorized database like Qdrant. Make a function to ingest the database using a CSV and a function to search the database."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ingest CSV Data into Vector Database (Priority: P1)

As a developer, I want to ingest data from a CSV file into a vector database so that I can later perform semantic searches on my data.

**Why this priority**: This is the foundational capability—without data ingestion, no searches can be performed. It establishes the core pipeline: read data → generate embeddings → store in vector DB.

**Independent Test**: Can be fully tested by providing a sample CSV file with text data, running the ingest function, and verifying records exist in the vector database with correct embeddings.

**Acceptance Scenarios**:

1. **Given** a CSV file with a text column and a Qdrant instance running, **When** I call the ingest function with the file path and column name, **Then** all rows are embedded and stored in the vector database with unique IDs.
2. **Given** a CSV file with 1000 rows, **When** I call the ingest function, **Then** the function processes all rows and reports progress/completion status.
3. **Given** a CSV file with some empty rows in the target column, **When** I call the ingest function, **Then** empty rows are skipped and logged, and valid rows are processed.

---

### User Story 2 - Search Vector Database (Priority: P2)

As a developer, I want to search the vector database using natural language queries so that I can find semantically similar content to my query.

**Why this priority**: Search is the primary value proposition after ingestion. Users need to retrieve relevant results from their stored data.

**Independent Test**: Can be tested by querying an already-populated database and verifying that returned results are semantically relevant to the query.

**Acceptance Scenarios**:

1. **Given** a populated vector database and a text query, **When** I call the search function, **Then** I receive a list of results ranked by similarity score.
2. **Given** a search query, **When** I specify a limit of N results, **Then** I receive at most N results.
3. **Given** a search query with a minimum similarity threshold, **When** results below the threshold exist, **Then** only results meeting the threshold are returned.

---

### User Story 3 - Configure Embedding Model (Priority: P3)

As a developer, I want to choose which HuggingFace model to use for embeddings so that I can optimize for my specific use case (speed, accuracy, domain).

**Why this priority**: Model selection enables customization but the library should work with sensible defaults. This is an enhancement over the core functionality.

**Independent Test**: Can be tested by initializing the library with different model names and verifying embeddings are generated using the specified model.

**Acceptance Scenarios**:

1. **Given** a valid HuggingFace model name, **When** I initialize the library with that model, **Then** embeddings are generated using the specified model.
2. **Given** no model is specified, **When** I initialize the library, **Then** a sensible default model is used (e.g., `sentence-transformers/all-MiniLM-L6-v2`).
3. **Given** an invalid model name, **When** I attempt to initialize, **Then** a clear error message indicates the model could not be loaded.

---

### User Story 4 - Image Embedding Support (Priority: P4)

As a developer, I want to embed images in addition to text so that I can build multimodal search applications.

**Why this priority**: Extends the library's capabilities beyond text. Requires different models (CLIP-based) and input handling.

**Independent Test**: Can be tested by providing image file paths, generating embeddings, and verifying they can be stored and searched.

**Acceptance Scenarios**:

1. **Given** a CSV with an image path column, **When** I call the ingest function specifying image mode, **Then** images are loaded, embedded, and stored.
2. **Given** an image file path as a search query, **When** I call the search function in image mode, **Then** similar images/content are returned.
3. **Given** a text query in a multimodal database, **When** I search, **Then** I can find relevant images based on text descriptions.

---

### Edge Cases

- What happens when the CSV file does not exist or is malformed?
- How does the system handle network failures when connecting to Qdrant?
- What happens when the HuggingFace model download fails or times out?
- How does the system handle very large CSV files that don't fit in memory?
- What happens when duplicate IDs are ingested?
- How does the system handle special characters or encoding issues in text?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Library MUST provide a function to ingest data from CSV files into a vector database
- **FR-002**: Library MUST provide a function to search the vector database using text queries
- **FR-003**: Library MUST support configurable HuggingFace embedding models
- **FR-004**: Library MUST support Qdrant as a vector database backend
- **FR-005**: Library MUST generate embeddings for text content using the configured model
- **FR-006**: Library MUST return search results with similarity scores
- **FR-007**: Library MUST support specifying which CSV column contains the content to embed
- **FR-008**: Library MUST support batch processing for efficient ingestion of large datasets
- **FR-009**: Library MUST provide clear error messages for common failure scenarios
- **FR-010**: Library MUST support configurable connection parameters for the vector database
- **FR-011**: Library MUST support image embeddings using CLIP-based models
- **FR-012**: Library MUST allow specifying the number of results to return from search
- **FR-013**: Library MUST allow filtering search results by minimum similarity threshold
- **FR-014**: Library MUST store original content metadata alongside embeddings for retrieval

### Key Entities

- **EmbeddingModel**: Represents the HuggingFace model used for generating embeddings. Attributes: model name, embedding dimension, modality (text/image/multimodal).
- **VectorStore**: Represents the connection to a vector database. Attributes: connection URL, collection name, distance metric.
- **Document**: Represents a single item to be embedded and stored. Attributes: unique ID, content (text or image path), metadata, embedding vector.
- **SearchResult**: Represents a single search result. Attributes: document ID, similarity score, original content, metadata.
- **IngestConfig**: Configuration for the ingestion process. Attributes: CSV path, content column, ID column (optional), batch size, metadata columns.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can ingest a 10,000-row CSV file in under 5 minutes on standard hardware
- **SC-002**: Search queries return results in under 500ms for databases with up to 100,000 vectors
- **SC-003**: Library can be installed and configured in under 5 minutes following documentation
- **SC-004**: 95% of common use cases (ingest + search) can be accomplished in under 10 lines of code
- **SC-005**: Error messages clearly indicate the cause and suggested resolution for all common failure modes
- **SC-006**: Library works with any sentence-transformers compatible model from HuggingFace
- **SC-007**: Memory usage during ingestion stays bounded regardless of CSV file size (streaming/batching)

## Assumptions

- Users have access to a running Qdrant instance (local or cloud)
- Users have Python 3.10+ installed
- Users have sufficient disk space for model downloads (~500MB for typical models)
- CSV files use UTF-8 encoding by default
- Network connectivity is available for HuggingFace model downloads

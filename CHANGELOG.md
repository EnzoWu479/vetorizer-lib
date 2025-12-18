# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project structure
- VetorizerClient for embedding and searching
- CSV ingestion with batch processing
- Text embeddings using sentence-transformers
- Image embeddings using CLIP
- Qdrant vector database integration
- Configurable HuggingFace models

## [0.1.0] - 2025-12-17

### Added

- Initial release
- `VetorizerClient` class for main functionality
- `ingest_csv()` for CSV data ingestion
- `search()` for semantic text search
- `ingest_images()` for image ingestion
- `search_by_image()` for image-based search
- Support for sentence-transformers models
- Support for CLIP models for multimodal search
- Qdrant integration (local and cloud)
- Comprehensive error handling with custom exceptions
- Type hints for all public APIs
- Google-style docstrings

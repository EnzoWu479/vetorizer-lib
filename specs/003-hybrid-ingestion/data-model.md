# Data Model: Ingestão Híbrida (Texto/Imagem)

See comprehensive data model in plan.md for entity definitions.

## Core Entities Summary

1. **IngestMode**: Enum (TEXT | IMAGE | HYBRID)
2. **CreateDatabaseRequest**: Database creation with file upload
3. **FileValidationResult**: Per-file validation result
4. **BatchValidationSummary**: Overall validation summary
5. **DatabaseMetadata**: Database configuration metadata
6. **IngestionResult**: Database creation result
7. **HybridVectorMetadata**: Vector composition metadata
8. **SearchQuery**: Extended search with hybrid support

Details documented in plan.md Project Structure section.

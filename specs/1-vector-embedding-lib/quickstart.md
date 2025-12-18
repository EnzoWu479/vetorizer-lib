# Quickstart: Vector Embedding Library

**Feature**: 1-vector-embedding-lib  
**Date**: 2025-12-17

## Installation

```bash
# Using uv (recommended)
uv add vetorizer-lib

# Or with pip
pip install vetorizer-lib
```

## Quick Start (5 minutes)

### 1. Basic Text Search

```python
from vetorizer_lib import VetorizerClient

# Initialize with defaults (in-memory Qdrant, MiniLM model)
client = VetorizerClient()

# Ingest your data
client.ingest_csv("products.csv", content_column="description")

# Search
results = client.search("comfortable running shoes", limit=5)
for r in results:
    print(f"[{r.score:.2f}] {r.content[:100]}...")
```

### 2. Sample CSV Format

Create `products.csv`:

```csv
id,title,description,category
1,Running Shoe X,Lightweight running shoe with cushioned sole,footwear
2,Hiking Boot Pro,Waterproof hiking boot for rough terrain,footwear
3,Casual Sneaker,Everyday comfortable sneaker for walking,footwear
```

### 3. Run It

```bash
# With uv
uv run python your_script.py

# Or directly
python your_script.py
```

---

## Common Use Cases

### Use Case 1: Product Search

```python
from vetorizer_lib import VetorizerClient

client = VetorizerClient(collection_name="products")

# Ingest with metadata
result = client.ingest_csv(
    "products.csv",
    content_column="description",
    id_column="id",
    metadata_columns=["title", "category", "price"]
)
print(f"Ingested {result.processed} products")

# Search with metadata in results
results = client.search("waterproof jacket")
for r in results:
    print(f"{r.metadata['title']}: ${r.metadata.get('price', 'N/A')}")
```

### Use Case 2: Document Search with Qdrant Server

```python
from vetorizer_lib import VetorizerClient

# Connect to running Qdrant instance
client = VetorizerClient(
    qdrant_url="http://localhost:6333",
    collection_name="documents"
)

# Ingest documents
client.ingest_csv("documents.csv", content_column="content")

# Search
results = client.search("machine learning best practices")
```

### Use Case 3: Image Search with CLIP

```python
from vetorizer_lib import VetorizerClient

# Use CLIP model for image embeddings
client = VetorizerClient(
    model_name="openai/clip-vit-base-patch32",
    collection_name="images"
)

# Ingest images (CSV contains paths to image files)
client.ingest_images("catalog.csv", image_column="image_path")

# Text-to-image search
results = client.search("sunset over mountains")

# Image-to-image search
results = client.search_by_image("query_image.jpg")
```

---

## Configuration Options

### Embedding Models

| Model | Use Case | Dimensions | Speed |
|-------|----------|------------|-------|
| `sentence-transformers/all-MiniLM-L6-v2` | General text (default) | 384 | Fast |
| `sentence-transformers/all-mpnet-base-v2` | Higher quality text | 768 | Medium |
| `openai/clip-vit-base-patch32` | Images + text | 512 | Medium |

### Qdrant Connection

```python
# In-memory (default, for testing)
client = VetorizerClient()

# Local file storage (persistent)
client = VetorizerClient(qdrant_path="./qdrant_data")

# Remote server
client = VetorizerClient(qdrant_url="http://localhost:6333")

# Qdrant Cloud
client = VetorizerClient(
    qdrant_url="https://xyz.cloud.qdrant.io",
    qdrant_api_key="your-api-key"
)
```

---

## Development Setup

```bash
# Clone and setup
git clone <repo>
cd vetorizer-lib

# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Type checking
uv run mypy vetorizer_lib

# Linting
uv run ruff check .
```

---

## Troubleshooting

### Model Download Fails

```python
# Error: ModelLoadError: Cannot download model
# Solution: Check internet connection, or pre-download:
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
```

### Qdrant Connection Refused

```python
# Error: ConnectionError: Cannot connect to Qdrant
# Solution: Start Qdrant or use in-memory mode:
docker run -p 6333:6333 qdrant/qdrant

# Or use in-memory for testing:
client = VetorizerClient()  # No qdrant_url = in-memory
```

### Out of Memory During Ingestion

```python
# Solution: Reduce batch size
client.ingest_csv("large.csv", content_column="text", batch_size=32)
```

---

## Next Steps

- See [API Contract](./contracts/api.md) for full API reference
- See [Data Model](./data-model.md) for entity definitions
- See [Research](./research.md) for technical decisions

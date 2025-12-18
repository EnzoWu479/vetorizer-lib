# Vetorizer-Lib

Embed text and images using HuggingFace models and store them in Qdrant vector database.

## Installation

```bash
# Using uv (recommended)
uv add vetorizer-lib

# Or with pip
pip install vetorizer-lib
```

## Quick Start

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

## Features

- **CSV Ingestion**: Batch process CSV files into vector embeddings
- **Semantic Search**: Find similar content using natural language queries
- **Model Selection**: Choose from any HuggingFace sentence-transformers model
- **Image Support**: Embed images using CLIP for multimodal search
- **Qdrant Backend**: Store vectors locally or in Qdrant Cloud
- **Web UI**: Browser-based interface for managing databases and searching

## Web UI

Launch the web interface to manage vector databases through your browser:

```bash
# Start the web server
vetorizer serve

# Or with custom host/port
vetorizer serve --host 0.0.0.0 --port 8080

# Or via Python module
python -m vetorizer_lib.web.cli serve
```

Then open http://localhost:8000 in your browser.

### Web UI Features

- **Upload CSV**: Drag-and-drop CSV files to create vector databases
- **Text Search**: Search databases using natural language queries
- **Image Search**: Upload images to find similar content
- **Compare**: Search multiple databases side-by-side
- **Manage**: Rename and delete databases

## Development

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

## Documentation

See [quickstart.md](specs/1-vector-embedding-lib/quickstart.md) for detailed usage examples.

## License

MIT

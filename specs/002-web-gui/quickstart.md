# Quickstart: Web GUI for Vector Database Management

**Feature**: 002-web-gui  
**Date**: 2024-12-17

## Overview

This guide helps you get started with the Vetorizer Web GUI - a graphical interface for managing vector databases, uploading CSV files, and performing semantic searches.

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- uv (Python package manager)
- pnpm or npm (Node package manager)

---

## Installation

### 1. Clone and Setup Backend

```bash
# Navigate to the web backend directory
cd web/backend

# Install dependencies with uv
uv sync

# Start the backend server
uv run uvicorn app.main:app --reload --port 8000
```

### 2. Setup Frontend

```bash
# Navigate to the web frontend directory
cd web/frontend

# Install dependencies
pnpm install

# Start the development server
pnpm dev
```

### 3. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (Swagger UI)

---

## Quick Start Guide

### Step 1: Upload a CSV and Create a Database

1. Click **"New Database"** on the home page
2. Select your CSV file (up to 100MB)
3. Choose the column containing text to embed
4. Enter a name for your database (e.g., "product-catalog")
5. Click **"Create Database"**
6. Wait for the progress bar to complete

**Example CSV format:**
```csv
id,title,description,category
1,Running Shoes,Comfortable lightweight running shoes for daily training,Footwear
2,Wireless Headphones,Noise-canceling Bluetooth headphones with 30hr battery,Electronics
3,Yoga Mat,Non-slip exercise mat for yoga and pilates,Fitness
```

### Step 2: Search Your Database

1. Go to the **Search** page
2. Select your database from the dropdown
3. Enter a natural language query (e.g., "comfortable shoes for exercise")
4. Click **Search**
5. View results ranked by similarity score

### Step 3: Search by Image

1. On the **Search** page, click the **Image** tab
2. Upload an image file (JPG, PNG, or WebP)
3. Select the database to search
4. Click **Search**
5. View semantically similar results

### Step 4: Compare Results Across Databases

1. Go to the **Compare** page
2. Select 2-4 databases to compare
3. Enter your search query
4. Click **Compare**
5. View side-by-side results from each database

### Step 5: Manage Databases

1. Go to the **Manage** page
2. View all your databases with document counts
3. Click **Rename** to change a database name
4. Click **Delete** to remove a database (requires confirmation)

---

## API Usage Examples

### List Databases

```bash
curl http://localhost:8000/api/databases
```

### Upload CSV

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@products.csv" \
  -F "database_name=my-products" \
  -F "content_column=description"
```

### Search by Text

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "database_ids": ["<database-uuid>"],
    "query_type": "text",
    "query_content": "comfortable running shoes",
    "limit": 10
  }'
```

### Search by Image

```bash
curl -X POST http://localhost:8000/api/search/image \
  -F "image=@photo.jpg" \
  -F "database_ids=<database-uuid>"
```

### Delete Database

```bash
curl -X DELETE http://localhost:8000/api/databases/<database-uuid>
```

---

## Configuration

### Backend Environment Variables

Create a `.env` file in `web/backend/`:

```env
# Qdrant storage path
QDRANT_PATH=./data/qdrant

# SQLite database path
SQLITE_PATH=./data/vetorizer.db

# Embedding model (default: all-MiniLM-L6-v2)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Max upload size in bytes (default: 100MB)
MAX_UPLOAD_SIZE=104857600

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000
```

### Frontend Environment Variables

Create a `.env` file in `web/frontend/`:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000/api
```

---

## Common Use Cases

### Product Catalog Search

Upload your product catalog CSV with descriptions, then search using natural language queries like:
- "waterproof hiking boots"
- "gifts under $50"
- "eco-friendly products"

### Document Search

Upload documents with text content to enable semantic search across your knowledge base:
- "how to reset password"
- "refund policy details"
- "shipping information"

### Image-Based Product Discovery

Upload product images to find similar items:
- Upload a photo of a dress to find similar styles
- Upload a furniture image to find matching pieces

### A/B Testing Embedding Models

Create multiple databases with the same data but different embedding models, then use the Compare feature to evaluate which model produces better search results.

---

## Troubleshooting

### "Database name already exists"

Choose a different name or check the "Overwrite" option to replace the existing database.

### "File too large"

CSV files must be under 100MB. Consider splitting large files or removing unnecessary columns.

### "Column not found"

Ensure the column name matches exactly (case-sensitive) with your CSV headers.

### Search returns no results

- Check that the database has documents (document count > 0)
- Try broader search terms
- Lower the minimum score threshold

### Slow ingestion

Large files take time to process. The progress bar shows real-time status. For 10,000 rows, expect ~2-3 minutes.

---

## Development

### Running Tests

```bash
# Backend tests
cd web/backend
uv run pytest

# Frontend tests
cd web/frontend
pnpm test
```

### Building for Production

```bash
# Backend - no build needed, use uvicorn directly

# Frontend
cd web/frontend
pnpm build
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

---

## Next Steps

- Read the [API Documentation](http://localhost:8000/docs) for detailed endpoint information
- Check the [Data Model](./data-model.md) for entity definitions
- Review the [Research](./research.md) for technical decisions

# Research: Ingestão Híbrida (Texto/Imagem)

**Feature Branch**: `003-hybrid-ingestion` | **Date**: 2025-12-18

## 1. UI Modal/Form Patterns for Database Creation

### Decision: HTMX + TailwindCSS Modal with Jinja2 Server-Side Rendering

**Rationale**:
- Consistent with existing vetorizer-lib web UI architecture
- Minimal JavaScript complexity (HTMX handles interactions)
- Server-side validation with rich feedback
- Progressive enhancement (works without JS)
- Accessibility built-in with proper ARIA attributes

**Best Practices**:
- **Overlay**: Semi-transparent backdrop (bg-black/50) with backdrop-blur
- **Focus Management**: Trap focus within modal, ESC key to close
- **Accessibility**: role="dialog", aria-labelledby, aria-modal="true"
- **Layout**: Vertical rhythm with consistent spacing (space-y-6)
- **Radio Buttons**: Visual cards with hover states and checked indicators
- **Collapsible Advanced Section**: Use native `<details>/<summary>` for simplicity, collapsed by default

---

## 2. Hybrid Vector Concatenation Strategy

### Decision: Text-First with Per-Modality Normalization

**Rationale**:
- Text embeddings (sentence-transformers) are NOT normalized (L2 norm: 3-8)
- Image embeddings (CLIP) ARE normalized (L2 norm = 1.0)
- Without normalization, image features contribute ~1/5th the weight
- Per-modality normalization ensures balanced contribution

**Critical Issue Identified**: Current implementation has normalization mismatch!

**Recommended Implementation**:
```python
import numpy as np

def concat_hybrid_vector_normalized(
    parts: HybridVectorParts,
    normalize_per_modality: bool = True
) -> list[float]:
    """Concatenate with proper normalization."""
    text_arr = np.array(parts.text_vector, dtype=np.float32)
    image_arr = np.array(parts.image_vector, dtype=np.float32)
    
    if normalize_per_modality:
        # Normalize each modality independently (RECOMMENDED)
        text_norm = text_arr / np.linalg.norm(text_arr)
        image_norm = image_arr / np.linalg.norm(image_arr)
        hybrid = np.concatenate([text_norm, image_norm])
    else:
        # Concatenate then normalize globally
        hybrid = np.concatenate([text_arr, image_arr])
        hybrid = hybrid / np.linalg.norm(hybrid)
    
    return hybrid.tolist()
```

**Concatenation Order**: Text-first (text → image) for consistency with text-heavy retrieval tasks

**Dimension Handling**:
- Simple concatenation preserves all information
- Current: 384d (text) + 512d (image) = 896d total
- Dimension imbalance acceptable (512/896 = 57% image weight)
- Document in metadata for compatibility checks

**Metadata Tracking**:
- Record hybrid_order, modalities, dimensions, models, normalization strategy
- Include schema_version and created_at timestamp
- Enable compatibility checks during search
- Support schema evolution

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Multi-vector/named vectors (Qdrant native) | Requires re-architecting collection creation and search; increases complexity |
| Dimension alignment via projection | Adds complexity for marginal gains; keep simple for v1 |
| No normalization | Image features contribute only 20% of similarity score (unbalanced) |

---

## 3. File Validation Strategy

### Decision: Server-Side Batch Validation Before Processing

**Rationale**:
- Client-side validation is bypassable (security)
- Batch validation prevents partial failures
- Detailed feedback improves UX
- Fail-fast approach saves processing time

**Validation Layers**:
1. **Extension Validation**: Check file extension against allowed list
2. **MIME Type Validation**: Use python-magic for content-based detection
3. **Size Validation**: Per-file and batch limits
4. **Content Validation**: CSV structure, image format, etc.
5. **Quota Validation**: User/database limits

**Allowed File Types**:
```python
ALLOWED_TYPES = {
    "text": {
        "extensions": {".csv", ".txt"},
        "mime_types": {"text/csv", "text/plain", "application/csv"}
    },
    "image": {
        "extensions": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"},
        "mime_types": {"image/jpeg", "image/png", "image/gif", ...}
    },
    "hybrid": {
        "extensions": {".csv"},
        "mime_types": {"text/csv", "text/plain"}
    }
}
```

**Validation Flow**:
1. User selects mode and uploads files
2. POST to `/api/validate-batch` endpoint
3. Server validates ALL files in parallel (max 5 concurrent)
4. Return detailed summary with per-file status
5. User reviews and can remove problematic files
6. User proceeds or cancels

**Quota Limits** (default):
- Max file size: 100MB per file
- Max batch size: 500MB total
- Max batch files: 50 files
- Max CSV rows: 1M rows per file

**Performance Optimization**:
- Parallel validation with asyncio
- Early termination on critical errors
- Streaming results for large batches
- Progress feedback via SSE

**Dependencies**: Add `python-magic-bin` (Windows) or `python-magic` (Linux/Mac) to pyproject.toml

---

## 4. Default Embedder Model Configuration

### Decision: Keep Text Model, Upgrade Image Model

**Current Configuration Assessment**:
- ✅ **Text**: `all-MiniLM-L6-v2` (384d) - Excellent choice, keep it
- ⚠️ **Image**: `clip-vit-base-patch32` (512d) - Recommend upgrading to patch16

**Recommended Configuration**:

**Text Embedder** (keep current):
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Size**: 22.7M parameters (~90MB, ~180MB FP16 in memory)
- **Performance**: ~56-58 MTEB score
- **Speed**: 5x faster than mpnet with minimal quality loss
- **Rationale**: Best balance for general-purpose production use

**Image Embedder** (upgrade recommended):
- **Model**: `openai/clip-vit-base-patch16` (upgrade from patch32)
- **Dimensions**: 512
- **Performance**: ~68.1% ImageNet (vs 63.3% for patch32)
- **Improvement**: +4.8% accuracy with same dimensions
- **Rationale**: Significant quality improvement, manageable speed tradeoff

**Alternative Configurations**:

| Profile | Text Model | Image Model | Use Case |
|---------|-----------|-------------|----------|
| **Fast** | all-MiniLM-L6-v2 (384d) | clip-vit-base-patch32 (512d) | Speed-critical |
| **Balanced** ⭐ | all-MiniLM-L6-v2 (384d) | clip-vit-base-patch16 (512d) | Recommended |
| **Quality** | all-mpnet-base-v2 (768d) | clip-vit-large-patch14 (768d) | Accuracy-critical |

**Model Loading Strategy**:
- Singleton pattern (load once at startup)
- HuggingFace cache: `~/.cache/huggingface/hub/`
- FP16 precision on GPU (2x memory saving, <1% quality loss)
- ONNX backend on CPU (2-3x speedup)
- Warm-up on startup with dummy inference

**Memory Requirements**:
- Text model: ~180MB (FP16)
- Image model: ~300MB (FP16)
- Total: ~500MB for both models
- Thread-safe: Single instance handles concurrent requests

---

## 5. Mode Selection Interface Design

### Decision: Explicit Radio Buttons with Visual Cards

**Rationale**:
- Clear intent (no ambiguity about mode)
- Equal discoverability (all three options visible)
- Visual feedback (checked state obvious)
- Aligns with FR-UI-002 requirement

**Implementation Pattern**:
```html
<label class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 
              has-[:checked]:border-blue-500 has-[:checked]:bg-blue-50">
  <input type="radio" name="ingest_mode" value="text" checked>
  <div class="ml-3">
    <div class="font-medium">Somente Texto</div>
    <div class="text-sm text-gray-500">CSV/TXT com conteúdo textual</div>
  </div>
</label>
```

**Dynamic Behavior**:
- Mode selection updates upload area instructions
- Advanced section shows relevant embedder options based on mode
- Validation logic adapts to selected mode

---

## 6. Database Creation Workflow

### Decision: Single-Step Transactional Operation

**Rationale**:
- Simplifies UX (one action completes everything)
- Atomic operation (all-or-nothing)
- Immediate feedback (database ready with data)
- Aligns with FR-UI-007 requirement

**Workflow Steps**:
1. User opens modal: "Criar Novo Banco de Dados"
2. User fills form: Name, mode selection, file upload
3. Optional: Expand advanced section for custom embedders
4. Submit form: POST to `/api/databases` with multipart data
5. Server validation: Batch validation of all files
6. Display summary: "X processados, Y ignorados, Z falhas" with details
7. User decision: Proceed or Cancel
8. If proceed: Create database + ingest valid documents (transactional)
9. Display result: Success with final statistics
10. Modal closes: Redirects to database list

---

## 7. Advanced Configuration Options

### Decision: Collapsible Section with Sensible Defaults

**Default Values**:
- Text model: `sentence-transformers/all-MiniLM-L6-v2`
- Image model: `openai/clip-vit-base-patch16`
- Normalization: `per_modality`
- Concatenation order: `text_first`
- Batch size: 100
- Enable FP16: true (GPU optimization)

**Advanced Section UI**:
- Collapsed by default (`<details>` element)
- Clear labels and help text
- Read-only fields for computed values (dimensions)
- Dropdowns for model selection (predefined list)
- Validation on submission

---

## 8. Error Handling and User Feedback

### Decision: Progressive Disclosure with Actionable Feedback

**Feedback Levels**:
1. **Summary Card**: Overall status (success/partial/failure)
2. **Statistics**: Valid/warnings/invalid counts
3. **Expandable Details**: Per-file accordion with errors/warnings
4. **Recommendations**: Actionable suggestions
5. **Remove Option**: Remove invalid files from batch
6. **Progress Indicators**: Real-time feedback during processing

**Response Format**:
```python
{
    "overall_status": "partial",  # valid/partial/invalid
    "summary": "✗ 2/10 files failed validation",
    "valid_files": 8,
    "invalid_files": 2,
    "files": [
        {
            "filename": "data.csv",
            "status": "valid",
            "errors": [],
            "warnings": ["Large file, may slow processing"]
        }
    ],
    "can_proceed": true,
    "recommendations": ["Remove 2 invalid files or fix errors"]
}
```

---

## Dependencies

**New Python Dependencies**:
```toml
[project.dependencies]
# Add to existing pyproject.toml
python-magic-bin = "^0.4.14"  # Windows MIME detection
python-magic = "^0.4.27"       # Linux/Mac MIME detection
numpy = "^1.24.0"              # Vector operations (already via torch)
```

**No additional frontend dependencies** (uses existing HTMX, TailwindCSS, hyperscript)

---

## Performance Considerations

**Model Loading**:
- Cold start: 2-5 seconds (first request loads models)
- Warm requests: <100ms overhead
- Memory: ~500MB for both models (FP16)

**Validation**:
- Parallel validation: 5 concurrent files
- Per-file: 50-200ms (depending on size)
- Batch of 10 files: ~1-2 seconds total

**Ingestion**:
- Text: ~2000-5000 docs/sec (batch=32, GPU)
- Image: ~500-1000 images/sec (batch=16, GPU)
- Hybrid: Limited by slower modality (image)

**Target Performance Goals**:
- Database creation + validation: <5s
- Ingestion of 100 documents: <30s (hybrid mode)
- Search with hybrid query: <500ms

---

## Security Considerations

1. **File Upload**: Use python-magic for MIME validation (prevent spoofing)
2. **Quota Limits**: Enforce per-user and per-database limits
3. **Input Sanitization**: Validate database names, column names
4. **Path Traversal**: Use safe path handling for uploaded files
5. **Resource Limits**: Timeout long-running operations
6. **Error Exposure**: Don't leak system paths in error messages

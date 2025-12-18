# Data Model: Ingestão Híbrida (Texto/Imagem)

**Feature**: 003-hybrid-ingestion  
**Date**: 2025-12-18

## Entities

### 1) Dataset / Vector Database

Representa uma “base” criada na UI e associada a uma collection.

**Atributos relevantes (conceituais)**:
- `id`: identificador único.
- `name`: nome amigável.
- `collection_name`: identificador da collection.
- `mode`: modo de ingestão associado à base.
  - Valores: `text`, `image`, `hybrid`
- `text_embedding_model`: identificador do modelo de texto (quando aplicável).
- `image_embedding_model`: identificador do modelo de imagem (quando aplicável).
- `embedding_dimensions`:
  - `text_dimension` (quando aplicável)
  - `image_dimension` (quando aplicável)
  - `hybrid_dimension` (quando aplicável; esperado = soma das dimensões)
- `document_count`.
- `status`.

**Regras de validação**:
- Se `mode=text`, `text_embedding_model` deve existir e `text_dimension > 0`.
- Se `mode=image`, `image_embedding_model` deve existir e `image_dimension > 0`.
- Se `mode=hybrid`, ambos modelos devem existir e `hybrid_dimension` deve ser compatível com as dimensões das modalidades.

---

### 2) Documento

Item lógico do dataset.

**Atributos relevantes (conceituais)**:
- `id`: id do documento.
- `text_content` (opcional).
- `image_reference` (opcional).
- `metadata`: mapa de chaves/valores.
- `vector`: vetor armazenado.
- `vector_modalities`: modalidades efetivamente usadas para gerar o vetor (`text`, `image`, `hybrid`).

**Regras de validação**:
- Conteúdo vazio deve ser tratado de forma previsível e relatável.
- Referência de imagem inválida deve ser tratada de forma previsível e relatável.

---

### 3) Upload Job

Acompanha processamento de ingestão.

**Atributos relevantes (conceituais)**:
- `id`.
- `database_id`.
- `status`.
- `progress_percent`.
- `documents_processed` / `documents_failed`.
- `error_message` (quando falhar).

---

## State transitions

### Upload Job

- `PENDING` -> `PROCESSING` -> `COMPLETED`
- `PENDING` -> `PROCESSING` -> `FAILED`

### Database Status

- `CREATING` -> `READY`
- `CREATING` -> `FAILED`
- `READY` -> `UPDATING` -> `READY`
- `READY` -> `DELETING`

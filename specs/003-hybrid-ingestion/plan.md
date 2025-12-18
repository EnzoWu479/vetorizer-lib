# Implementation Plan: Ingestão Híbrida (Texto/Imagem)

**Branch**: `003-hybrid-ingestion` | **Date**: 2025-12-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-hybrid-ingestion/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Adicionar suporte a ingestão e busca **híbrida** (texto+imagem) em que cada documento pode ser vetorizado por duas modalidades e o vetor final seja composto por concatenação determinística. A UI Web deve permitir selecionar o modo de ingestão (texto, imagem, híbrido) e executar busca compatível (texto, imagem, híbrida).

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: sentence-transformers, transformers, torch, Pillow, qdrant-client, FastAPI, Jinja2  
**Storage**: Qdrant (local path ou remoto)  
**Testing**: pytest (com mocks para modelos e Qdrant)  
**Target Platform**: Biblioteca Python + Web UI em browsers modernos  
**Project Type**: Python library com UI web integrada (FastAPI + templates)  
**Performance Goals**: Ingestão de CSV de 10K linhas em minutos (dependente de modelo) com feedback de progresso; busca interativa com latência percebida baixa na UI  
**Constraints**: Vetores em coleção Qdrant possuem dimensão fixa; ingestões existentes texto/imagem devem continuar funcionais  
**Scale/Scope**: Uso single-node; múltiplas “databases” mapeadas para collections

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality & Testability | PASS | Garantir DI/mocks para embedder e store; evitar `Any` sem justificativa |
| II. Testing Standards | PASS | Planejar unit/integration/contract tests; testes determinísticos |
| III. User Experience Consistency | PASS | UI mantém padrões existentes (tabs, feedback de upload/busca) |
| IV. Performance Requirements | PASS | Operações longas com progress; evitar travar UI |
| V. Documentation Standards | PASS | Novas APIs e fluxos documentados; exemplos de uso |

**Quality Gates**:
- Linting: ruff
- Type Safety: mypy (strict)
- Testing: pytest
- Documentation: docstrings para APIs públicas

## Project Structure

### Documentation (this feature)

```text
specs/003-hybrid-ingestion/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
vetorizer_lib/
├── client.py                 # Biblioteca: ingestão/busca (texto e imagem)
├── embedders/                # Embedders de texto e imagem
├── ingest/                   # Leitura e batching de CSV
├── models/                   # Dataclasses e configurações
├── stores/                   # Store Qdrant
└── web/                      # UI Web (FastAPI + templates)
    ├── app.py
    ├── cli.py
    ├── routes/
    │   ├── upload.py         # Upload/ingestão via UI
    │   └── search.py         # Busca via UI
    ├── services/
    │   ├── upload_service.py # Orquestra ingestão
    │   └── search_service.py # Orquestra busca
    ├── models/
    │   ├── schemas.py        # Contratos Pydantic
    │   └── metadata_store.py # Metadados de databases/jobs em Qdrant
    └── templates/
        ├── partials/
        │   └── upload_form.html
        └── search.html

tests/
├── unit/
├── integration/
└── contract/
```

**Structure Decision**: Manter arquitetura integrada (biblioteca + UI no mesmo pacote). A feature adiciona capacidade híbrida na biblioteca e expõe novos campos/fluxos nas rotas e templates da UI.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
